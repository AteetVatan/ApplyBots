"""Agent endpoints.

Standards: python_clean.mdc
- Async operations
- Proper error handling
"""

import structlog
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status

from app.api.deps import AppSettings, CurrentUser, DBSession
from app.schemas.agent import (
    BulkApplyRequest,
    ChatRequest,
    ChatResponse,
    OptimizeRequest,
    OptimizeResponse,
)

router = APIRouter()
logger = structlog.get_logger()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agents(
    request: ChatRequest,
    current_user: CurrentUser,
    db: DBSession,
    settings: AppSettings,
) -> ChatResponse:
    """Send a message to the agent system."""
    try:
        from app.agents.workflows import JobApplicationWorkflow
    except ImportError as e:
        logger.warning("agent_workflow_not_available", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent system is not available. Please try again later.",
        )

    try:
        workflow = JobApplicationWorkflow(
            user_id=current_user.id,
            db_session=db,
            settings=settings,
        )

        response = await workflow.process_message(
            message=request.message,
            session_id=request.session_id,
        )

        return ChatResponse(
            message=response.content,
            session_id=response.session_id,
            agents_involved=response.agents_involved,
            actions_taken=response.actions_taken,
        )

    except Exception as e:
        logger.error("agent_chat_error", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent system error",
        )


@router.post("/optimize-resume", response_model=OptimizeResponse)
async def optimize_resume(
    request: OptimizeRequest,
    current_user: CurrentUser,
    db: DBSession,
    settings: AppSettings,
) -> OptimizeResponse:
    """Optimize resume for a specific job."""
    from app.agents.workflows import JobApplicationWorkflow
    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.repositories.resume import SQLResumeRepository

    job_repo = SQLJobRepository(session=db)
    resume_repo = SQLResumeRepository(session=db)

    # Validate job and resume exist
    job = await job_repo.get_by_id(request.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    resume = await resume_repo.get_by_id(request.resume_id)
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    try:
        workflow = JobApplicationWorkflow(
            user_id=current_user.id,
            db_session=db,
            settings=settings,
        )

        result = await workflow.optimize_resume(
            resume_id=request.resume_id,
            job_id=request.job_id,
        )

        return OptimizeResponse(
            original_match_score=result.original_score,
            optimized_match_score=result.optimized_score,
            suggestions=result.suggestions,
            tailored_summary=result.tailored_summary,
            highlighted_skills=result.highlighted_skills,
        )

    except Exception as e:
        logger.error(
            "resume_optimization_error",
            error=str(e),
            user_id=current_user.id,
            resume_id=request.resume_id,
            job_id=request.job_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resume optimization failed",
        )


@router.post("/bulk-apply", status_code=status.HTTP_202_ACCEPTED)
async def bulk_apply(
    request: BulkApplyRequest,
    current_user: CurrentUser,
    db: DBSession,
    settings: AppSettings,
) -> dict[str, str]:
    """Queue bulk application to multiple jobs."""
    from app.core.services.plan_gating import PlanGatingService
    from app.infra.db.repositories.subscription import SQLSubscriptionRepository
    from app.workers.application_submitter import bulk_apply_task

    # Check plan limits
    sub_repo = SQLSubscriptionRepository(session=db)
    subscription = await sub_repo.get_by_user_id(current_user.id)

    if subscription:
        gating = PlanGatingService()
        remaining = gating.get_remaining_today(subscription=subscription)

        if len(request.job_ids) > remaining:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Exceeds daily limit. Only {remaining} applications remaining today.",
            )

    # Queue bulk apply task
    bulk_apply_task.delay(
        user_id=current_user.id,
        job_ids=request.job_ids,
        resume_id=request.resume_id,
        auto_submit=request.auto_submit,
    )

    logger.info(
        "bulk_apply_queued",
        user_id=current_user.id,
        job_count=len(request.job_ids),
        auto_submit=request.auto_submit,
    )

    return {"status": f"Queued {len(request.job_ids)} applications"}


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    db: DBSession,
    settings: AppSettings,
) -> None:
    """WebSocket endpoint for streaming agent chat."""
    await websocket.accept()

    # Simple token auth from query params
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    try:
        from app.infra.auth.jwt import decode_access_token
        from app.infra.db.repositories.user import SQLUserRepository

        payload = decode_access_token(
            token=token,
            secret_key=settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        )

        user_repo = SQLUserRepository(session=db)
        user = await user_repo.get_by_id(payload["sub"])

        if not user:
            await websocket.close(code=4001, reason="User not found")
            return

    except Exception as e:
        logger.warning("websocket_auth_failed", error=str(e))
        await websocket.close(code=4001, reason="Invalid token")
        return

    from app.agents.workflows import JobApplicationWorkflow

    workflow = JobApplicationWorkflow(
        user_id=user.id,
        db_session=db,
        settings=settings,
    )

    try:
        while True:
            message = await websocket.receive_text()

            async for response in workflow.stream_process(message):
                await websocket.send_json({
                    "type": "agent_response",
                    "agent": response.agent_name,
                    "content": response.content,
                    "is_final": response.is_final,
                })

    except WebSocketDisconnect:
        logger.info("websocket_disconnected", user_id=user.id)
    except Exception as e:
        logger.error("websocket_error", error=str(e), user_id=user.id)
        await websocket.close(code=1011, reason="Internal error")
