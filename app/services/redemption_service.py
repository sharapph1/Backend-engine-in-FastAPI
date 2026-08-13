from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.redemption import Redemption
from app.schemas.redemption import RedemptionCreate, RedemptionResponse, RedemptionListResponse
from app.services.wallet_service import WalletService

class RedemptionService:

    @staticmethod
    def create_redemption(db: Session, user: User, data: RedemptionCreate) -> RedemptionResponse:
        # Deduct coins from wallet, raises HTTPException if insufficient
        WalletService.deduct(db, user, data.coins)
        
        redemption = Redemption(
            user_id=user.id,
            coins=data.coins,
            status="pending",
            upi_id=data.upi_id,
            full_name=data.full_name
        )
        db.add(redemption)
        db.commit()
        db.refresh(redemption)
        
        return RedemptionResponse.model_validate(redemption)

    @staticmethod
    def get_redemptions(db: Session, user: User) -> RedemptionListResponse:
        query = db.query(Redemption).filter(Redemption.user_id == user.id).order_by(Redemption.created_at.desc())
        total = query.count()
        items = query.all()
        
        return RedemptionListResponse(
            items=[RedemptionResponse.model_validate(item) for item in items],
            total=total
        )
