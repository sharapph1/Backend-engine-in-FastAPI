import secrets
import string

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.referral import Referral
from app.models.user import User
from app.schemas.referral import (
    ReferralClaimRequest,
    ReferralResponse,
    ReferralStatsResponse,
    ReferralUser,
)


class ReferralService:

    @staticmethod
    def generate_refer_id() -> str:
        chars = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(chars) for _ in range(8))

    @staticmethod
    async def get_or_create_refer_id(db: Session, user: User) -> str:
        if not user.refer_id:
            user.refer_id = ReferralService.generate_refer_id()
            db.commit()
            db.refresh(user)
        return user.refer_id

    @staticmethod
    async def claim_referral(
        db: Session,
        user: User,
        data: ReferralClaimRequest,
    ) -> ReferralResponse:
        referral_code = data.referral_code.strip()

        referrer = db.query(User).filter(
            (User.refer_id == referral_code) | (User.username == referral_code)
        ).first()

        if not referrer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referral code or user not found.",
            )

        if referrer.id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot use your own referral code.",
            )

        already_referred = db.query(Referral).filter(
            Referral.referred_user_id == user.id
        ).first()

        if already_referred:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already claimed a referral code.",
            )

        referral = Referral(
            referrer_id=referrer.id,
            referred_user_id=user.id,
        )

        db.add(referral)
        db.commit()
        db.refresh(referral)

        return ReferralResponse.model_validate(referral)

    @staticmethod
    async def get_referral_stats(
        db: Session,
        user: User,
    ) -> ReferralStatsResponse:
        refer_id = await ReferralService.get_or_create_refer_id(db, user)

        referrals = db.query(Referral).filter(
            Referral.referrer_id == user.id
        ).all()

        referred_users = []
        for ref in referrals:
            referred_user = db.query(User).filter(User.id == ref.referred_user_id).first()
            if referred_user:
                referred_users.append(
                    ReferralUser(
                        id=referred_user.id,
                        username=referred_user.username,
                        created_at=referred_user.created_at,
                    )
                )

        return ReferralStatsResponse(
            referral_code=refer_id,
            total_referrals=len(referred_users),
            referred_users=referred_users,
        )
