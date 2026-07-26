from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.streak import ClaimStreakResponse, StreakResponse
from app.services.streak_service import StreakService

router = APIRouter(
    prefix="/streaks",
    tags=["Streaks"],
)


@router.get(
    "/me",
    response_model=StreakResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await StreakService.get_user_streak(db=db, user=current_user)


@router.post(
    "/claim",
    response_model=ClaimStreakResponse,
    status_code=status.HTTP_200_OK,
)
async def claim_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await StreakService.claim_daily_streak(db=db, user=current_user)
