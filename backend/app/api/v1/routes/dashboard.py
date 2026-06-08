from __future__ import annotations

from app.api.v1.dependencies.auth import get_current_user
from app.core.database.session import get_session
from app.domains.dashboard.service import DashboardService
from app.domains.movements.models import AssetMovement
from app.domains.movements.schemas import MovementRead
from app.domains.users.models import User
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def summary(session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> dict[str, int]:
    return await DashboardService(session).summary()


@router.get("/assets-by-status")
async def assets_by_status(session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> list[dict[str, str | int]]:
    return await DashboardService(session).group_by("status")


@router.get("/assets-by-type")
async def assets_by_type(session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> list[dict[str, str | int]]:
    return await DashboardService(session).group_by("asset_type")


@router.get("/recent-movements", response_model=list[MovementRead])
async def recent_movements(session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> list[AssetMovement]:
    return await DashboardService(session).recent_movements()
