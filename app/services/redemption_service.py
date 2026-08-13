from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.redemption import Redemption
from app.models.user import User
from app.schemas.redemption import (
    RedemptionCreate,
    RedemptionListResponse,
    RedemptionResponse,
)
from app.services.wallet_service import WalletService


class RedemptionService:

    @staticmethod
    async def create_redemption(
        db: Session,
        user: User,
        data: RedemptionCreate,
    ) -> RedemptionResponse:
        # Deduct from wallet first — raises HTTP 400 if insufficient
        await WalletService.deduct(db=db, user=user, amount=data.coins)

        redemption = Redemption(
            user_id=user.id,
            coins=data.coins,
            status="pending",
        )
        db.add(redemption)
        db.commit()
        db.refresh(redemption)

        return RedemptionResponse.model_validate(redemption)

    @staticmethod
    async def get_user_redemptions(
        db: Session,
        user: User,
    ) -> RedemptionListResponse:
        redemptions = (
            db.query(Redemption)
            .filter(Redemption.user_id == user.id)
            .order_by(Redemption.created_at.desc())
            .all()
        )
        items = [RedemptionResponse.model_validate(r) for r in redemptions]
        return RedemptionListResponse(items=items, total=len(items))
