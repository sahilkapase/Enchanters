from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_agent
from app.schemas.agent import (
    AgentLoginRequest, AgentTokenResponse,
    FarmerLookupRequest, FarmerLookupResponse,
    RequestAccessRequest, RequestAccessResponse,
    VerifyAccessRequest, VerifyAccessResponse,
    AgentSessionDetail, AgentActivityItem,
)
from app.schemas.farmer import FarmerResponse
from app.schemas.scheme import FormGenerateResponse
from app.services import agent_service, scheme_service, insurance_service
from app.models.agent import Agent

router = APIRouter(prefix="/service", tags=["Service Portal"])


@router.post("/auth/login", response_model=AgentTokenResponse)
async def agent_login(body: AgentLoginRequest, db: AsyncSession = Depends(get_db)):
    return await agent_service.login_agent(db, body.phone, body.password)


@router.post("/lookup", response_model=FarmerLookupResponse)
async def lookup_farmer(
    body: FarmerLookupRequest,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    return await agent_service.lookup_farmer(db, body.query)


@router.post("/request-access", response_model=RequestAccessResponse)
async def request_access(
    body: RequestAccessRequest,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    return await agent_service.request_access(db, agent.id, body.farmer_identifier, body.purpose)


@router.post("/verify-access", response_model=VerifyAccessResponse)
async def verify_access(
    body: VerifyAccessRequest,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    return await agent_service.verify_access(db, body.session_id, body.otp)


@router.get("/session/{session_id}", response_model=AgentSessionDetail)
async def get_session(
    session_id: UUID,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    return await agent_service.get_session_detail(db, session_id, agent.id)


@router.get("/session/{session_id}/farmer", response_model=FarmerResponse)
async def get_farmer_in_session(
    session_id: UUID,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    return await agent_service.get_farmer_for_session(db, session_id, agent.id)


@router.post("/session/{session_id}/generate-form", response_model=FormGenerateResponse)
async def generate_form_in_session(
    session_id: UUID,
    scheme_id: UUID | None = None,
    plan_id: UUID | None = None,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    farmer = await agent_service.get_farmer_for_session(db, session_id, agent.id)

    if scheme_id:
        return await scheme_service.generate_scheme_form(
            db, scheme_id, farmer,
            generated_by="agent",
            agent_name=agent.name,
            agent_session_id=session_id,
        )
    elif plan_id:
        return await insurance_service.generate_insurance_form(
            db, plan_id, farmer,
            generated_by="agent",
            agent_session_id=session_id,
        )
    else:
        from app.core.exceptions import BadRequestException
        raise BadRequestException("Either scheme_id or plan_id is required")


@router.post("/session/{session_id}/end")
async def end_session(
    session_id: UUID,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    return await agent_service.end_session(db, session_id, agent.id)


@router.get("/activity", response_model=list[AgentActivityItem])
async def get_activity(
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    return await agent_service.get_activity(db, agent.id)
