from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.daily_usage import AdImpressionLog, DailyUsageResponse
from app.services.daily_usage_service import DailyUsageService

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.post(
    "/ads",
    response_model=DailyUsageResponse,
    status_code=status.HTTP_200_OK,
)
async def log_ad_impression(
    data: AdImpressionLog,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await DailyUsageService.log_ad_impression(
        db=db, user=current_user, data=data
    )


@router.get(
    "/me",
    response_model=DailyUsageResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_daily_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await DailyUsageService.get_daily_usage(
        db=db, user=current_user
    )
