from uuid import UUID
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import async_session_factory
from app.models.farmer import Farmer
from app.models.agent import Agent
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
import logging

logger = logging.getLogger(__name__)

security_scheme = HTTPBearer()


async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_farmer(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> Farmer:
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired token")

    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid token type")

    if payload.get("role") != "farmer":
        raise ForbiddenException("Farmer access required")

    farmer_uuid = payload.get("sub")
    if not farmer_uuid:
        raise UnauthorizedException("Invalid token payload")

    try:
        uid = UUID(farmer_uuid)
    except ValueError:
        raise UnauthorizedException("Invalid token payload")

    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Farmer)
        .options(
            selectinload(Farmer.profile),
            selectinload(Farmer.crops),
            selectinload(Farmer.documents),
        )
        .where(Farmer.id == uid)
    )
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise UnauthorizedException("Farmer not found")

    return farmer


async def get_current_agent(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> Agent:
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired token")

    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid token type")

    if payload.get("role") != "agent":
        raise ForbiddenException("Agent access required")

    agent_uuid = payload.get("sub")
    if not agent_uuid:
        raise UnauthorizedException("Invalid token payload")

    try:
        uid = UUID(agent_uuid)
    except ValueError:
        raise UnauthorizedException("Invalid token payload")

    result = await db.execute(select(Agent).where(Agent.id == uid))
    agent = result.scalar_one_or_none()
    if not agent:
        raise UnauthorizedException("Agent not found")
    if not agent.is_active:
        raise ForbiddenException("Agent account is deactivated")

    return agent
