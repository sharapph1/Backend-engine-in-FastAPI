from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.wallet import WalletResponse
from app.services.wallet_service import WalletService

router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"],
)


@router.get(
    "/me",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
    summary="Get my wallet",
    description="Returns the authenticated user's coin balance. Creates the wallet automatically if it doesn't exist yet.",
)
async def get_my_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await WalletService.get_wallet(db=db, user=current_user)
