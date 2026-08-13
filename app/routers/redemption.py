from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.redemption import RedemptionCreate, RedemptionResponse, RedemptionListResponse
from app.services.redemption_service import RedemptionService

router = APIRouter(
    prefix="/redemptions",
    tags=["Redemptions"],
)

@router.post(
    "",
    response_model=RedemptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create redemption request",
    description="Create a new redemption request, deducting coins from the wallet.",
)
async def create_redemption(
    data: RedemptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RedemptionService.create_redemption(db=db, user=current_user, data=data)

@router.get(
    "/me",
    response_model=RedemptionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get my redemptions",
    description="Fetch the current user's redemption requests.",
)
async def get_my_redemptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RedemptionService.get_redemptions(db=db, user=current_user)
