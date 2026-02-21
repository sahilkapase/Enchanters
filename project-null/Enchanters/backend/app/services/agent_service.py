from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from app.models.agent import Agent, AgentSession
from app.models.farmer import Farmer
from app.core.security import verify_password, create_access_token
from app.core.otp import send_and_store_otp, verify_otp
from app.core.constants import AgentSessionStatus, AGENT_SESSION_TTL_MINUTES
from app.core.exceptions import (
    NotFoundException, UnauthorizedException, ForbiddenException,
    BadRequestException, SessionExpiredException,
)
from app.external.sms import send_agent_access_sms
import logging

logger = logging.getLogger(__name__)


async def login_agent(db: AsyncSession, phone: str, password: str) -> dict:
    result = await db.execute(select(Agent).where(Agent.phone == phone))
    agent = result.scalar_one_or_none()
    if not agent:
        raise UnauthorizedException("Invalid credentials")
    if not agent.is_active:
        raise ForbiddenException("Agent account is deactivated")
    if not verify_password(password, agent.password_hash):
        raise UnauthorizedException("Invalid credentials")

    token = create_access_token(
        str(agent.id),
        extra_claims={"role": "agent", "center": agent.center_name},
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "agent_name": agent.name,
        "center_name": agent.center_name,
    }


async def lookup_farmer(db: AsyncSession, query: str) -> dict:
    """Look up farmer by farmer_id or phone number."""
    result = await db.execute(
        select(Farmer).where(
            or_(Farmer.farmer_id == query, Farmer.phone == query)
        )
    )
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise NotFoundException("Farmer")

    phone = farmer.phone
    masked = f"{phone[:2]}{'*' * (len(phone) - 4)}{phone[-2:]}"

    return {
        "name": farmer.name,
        "phone_masked": masked,
        "farmer_id": farmer.farmer_id,
        "district": farmer.district,
        "state": farmer.state,
    }


async def request_access(
    db: AsyncSession,
    agent_id: UUID,
    farmer_identifier: str,
    purpose: str,
) -> dict:
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundException("Agent")

    farmer_result = await db.execute(
        select(Farmer).where(
            or_(Farmer.farmer_id == farmer_identifier, Farmer.phone == farmer_identifier)
        )
    )
    farmer = farmer_result.scalar_one_or_none()
    if not farmer:
        raise NotFoundException("Farmer")

    session = AgentSession(
        agent_id=agent_id,
        farmer_id=farmer.id,
        purpose=purpose,
        status=AgentSessionStatus.ACTIVE,
    )
    db.add(session)
    await db.flush()

    otp = await send_and_store_otp(farmer.phone, "agent_access")
    await send_agent_access_sms(
        farmer.phone, otp, agent.name, agent.center_name or "Service Center", purpose
    )

    logger.info("Access requested by agent %s for farmer %s", agent.name, farmer.farmer_id)
    return {
        "session_id": session.id,
        "otp_sent": True,
        "message": f"OTP sent to farmer's phone for verification",
    }


async def verify_access(db: AsyncSession, session_id: UUID, otp: str) -> dict:
    result = await db.execute(
        select(AgentSession).where(AgentSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundException("Session")

    farmer_result = await db.execute(select(Farmer).where(Farmer.id == session.farmer_id))
    farmer = farmer_result.scalar_one_or_none()
    if not farmer:
        raise NotFoundException("Farmer")

    await verify_otp(farmer.phone, otp, "agent_access")

    now = datetime.now(timezone.utc)
    session.otp_verified_at = now
    session.session_start = now
    session.status = AgentSessionStatus.ACTIVE
    await db.flush()

    expires_at = now + timedelta(minutes=AGENT_SESSION_TTL_MINUTES)
    logger.info("Agent access verified for session %s", session_id)
    return {
        "session_id": session.id,
        "farmer_id": farmer.farmer_id,
        "farmer_name": farmer.name,
        "expires_at": expires_at,
        "message": f"Access granted for {AGENT_SESSION_TTL_MINUTES} minutes",
    }


def _check_session_active(session: AgentSession) -> None:
    if session.status == AgentSessionStatus.ENDED:
        raise SessionExpiredException()

    if session.session_start:
        expiry = session.session_start + timedelta(minutes=AGENT_SESSION_TTL_MINUTES)
        if datetime.now(timezone.utc) > expiry:
            session.status = AgentSessionStatus.EXPIRED
            raise SessionExpiredException()
    else:
        raise BadRequestException("Session not yet verified")


async def get_session_detail(db: AsyncSession, session_id: UUID, agent_id: UUID) -> dict:
    result = await db.execute(
        select(AgentSession).where(AgentSession.id == session_id, AgentSession.agent_id == agent_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundException("Session")

    _check_session_active(session)

    farmer_result = await db.execute(select(Farmer).where(Farmer.id == session.farmer_id))
    farmer = farmer_result.scalar_one_or_none()

    time_remaining = 0
    if session.session_start:
        expiry = session.session_start + timedelta(minutes=AGENT_SESSION_TTL_MINUTES)
        remaining = (expiry - datetime.now(timezone.utc)).total_seconds()
        time_remaining = max(0, int(remaining))

    return {
        "id": session.id,
        "agent_id": session.agent_id,
        "farmer_id": session.farmer_id,
        "farmer_name": farmer.name if farmer else None,
        "purpose": session.purpose,
        "otp_verified_at": session.otp_verified_at,
        "session_start": session.session_start,
        "session_end": session.session_end,
        "forms_downloaded": session.forms_downloaded or [],
        "actions_taken": session.actions_taken or [],
        "status": session.status.value if hasattr(session.status, 'value') else str(session.status),
        "time_remaining_seconds": time_remaining,
    }


async def get_farmer_for_session(db: AsyncSession, session_id: UUID, agent_id: UUID) -> Farmer:
    result = await db.execute(
        select(AgentSession).where(AgentSession.id == session_id, AgentSession.agent_id == agent_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundException("Session")

    _check_session_active(session)
    await db.flush()

    farmer_result = await db.execute(
        select(Farmer)
        .options(
            selectinload(Farmer.profile),
            selectinload(Farmer.crops),
            selectinload(Farmer.documents),
        )
        .where(Farmer.id == session.farmer_id)
    )
    farmer = farmer_result.scalar_one_or_none()
    if not farmer:
        raise NotFoundException("Farmer")

    actions = session.actions_taken or []
    actions.append({"action": "viewed_farmer_data", "at": datetime.now(timezone.utc).isoformat()})
    session.actions_taken = actions
    await db.flush()

    return farmer


async def end_session(db: AsyncSession, session_id: UUID, agent_id: UUID) -> dict:
    result = await db.execute(
        select(AgentSession).where(AgentSession.id == session_id, AgentSession.agent_id == agent_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundException("Session")

    session.status = AgentSessionStatus.ENDED
    session.session_end = datetime.now(timezone.utc)
    await db.flush()

    logger.info("Session %s ended by agent", session_id)
    return {"message": "Session ended"}


async def get_activity(db: AsyncSession, agent_id: UUID) -> list[dict]:
    result = await db.execute(
        select(AgentSession, Farmer.farmer_id, Farmer.name)
        .join(Farmer, AgentSession.farmer_id == Farmer.id)
        .where(AgentSession.agent_id == agent_id)
        .order_by(AgentSession.session_start.desc())
    )
    rows = result.all()

    return [
        {
            "id": session.id,
            "farmer_id": fid,
            "farmer_name": fname,
            "purpose": session.purpose,
            "session_start": session.session_start,
            "session_end": session.session_end,
            "status": session.status.value if hasattr(session.status, 'value') else str(session.status),
            "forms_count": len(session.forms_downloaded or []),
        }
        for session, fid, fname in rows
    ]
