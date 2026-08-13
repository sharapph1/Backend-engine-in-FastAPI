from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.wallet import UserWallet
from app.schemas.wallet import WalletResponse


class WalletService:

    @staticmethod
    def get_or_create(db: Session, user: User) -> UserWallet:
        wallet = db.query(UserWallet).filter(UserWallet.user_id == user.id).first()
        if not wallet:
            wallet = UserWallet(user_id=user.id, coins=0)
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
        return wallet

    @staticmethod
    async def get_wallet(db: Session, user: User) -> WalletResponse:
        wallet = WalletService.get_or_create(db, user)
        return WalletResponse(
            user_id=wallet.user_id,
            coins=wallet.coins,
            updated_at=wallet.updated_at,
        )

    @staticmethod
    async def credit(db: Session, user: User, amount: int) -> UserWallet:
        wallet = WalletService.get_or_create(db, user)
        wallet.coins += amount
        wallet.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(wallet)
        return wallet

    @staticmethod
    async def deduct(db: Session, user: User, amount: int) -> UserWallet:
        wallet = WalletService.get_or_create(db, user)
        if wallet.coins < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. You have {wallet.coins} coins.",
            )
        wallet.coins -= amount
        wallet.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(wallet)
        return wallet
