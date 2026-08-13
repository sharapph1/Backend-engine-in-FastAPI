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
    def get_balance(db: Session, user: User) -> WalletResponse:
        wallet = WalletService.get_or_create(db, user)
        return WalletResponse.model_validate(wallet)

    @staticmethod
    def credit(db: Session, user: User, amount: int) -> UserWallet:
        wallet = WalletService.get_or_create(db, user)
        wallet.coins += amount
        wallet.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(wallet)
        return wallet

    @staticmethod
    def deduct(db: Session, user: User, amount: int) -> UserWallet:
        wallet = WalletService.get_or_create(db, user)
        if wallet.coins < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance",
            )
        wallet.coins -= amount
        wallet.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(wallet)
        return wallet
