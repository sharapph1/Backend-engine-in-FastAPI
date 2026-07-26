from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.referral import (
    ReferralClaimRequest,
    ReferralResponse,
    ReferralStatsResponse,
)
from app.services.referral_service import ReferralService

router = APIRouter(
    prefix="/referrals",
    tags=["Referrals"],
)


@router.get(
    "/me",
    response_model=ReferralStatsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_referral_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ReferralService.get_referral_stats(db=db, user=current_user)


@router.post(
    "/claim",
    response_model=ReferralResponse,
    status_code=status.HTTP_201_CREATED,
)
async def claim_referral(
    data: ReferralClaimRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ReferralService.claim_referral(
        db=db, user=current_user, data=data
    )
