from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.referral import Referral
from app.models.streak import Streak
from app.models.user import User
from app.schemas.streak import ClaimStreakResponse, StreakResponse


class StreakService:

    @staticmethod
    def calculate_coupon_tier(current_streak: int, referral_count: int) -> str | None:
        if current_streak >= 30 and referral_count >= 5:
            return "Star"
        if current_streak >= 20 and referral_count >= 10:
            return "Diamond"
        if current_streak >= 12 and referral_count >= 5:
            return "Gold"
        if current_streak >= 5 and referral_count >= 3:
            return "Silver"
        return None

    @staticmethod
    def is_kyc_eligible(streak: Streak | None) -> bool:
        if not streak or streak.current_streak < 3:
            return False
        if not streak.last_claim_date:
            return False
        today = date.today()
        # KYC is active if current streak >= 3 and last claim was today or yesterday
        return (today - streak.last_claim_date).days <= 1

    @staticmethod
    async def get_user_streak(db: Session, user: User) -> StreakResponse:
        streak = db.query(Streak).filter(Streak.user_id == user.id).first()

        if not streak:
            streak = Streak(
                user_id=user.id,
                current_streak=0,
                highest_streak=0,
                last_claim_date=None,
            )
            db.add(streak)
            db.commit()
            db.refresh(streak)

        referral_count = db.query(Referral).filter(Referral.referrer_id == user.id).count()
        coupon_tier = StreakService.calculate_coupon_tier(streak.current_streak, referral_count)
        kyc_eligible = StreakService.is_kyc_eligible(streak)

        return StreakResponse(
            id=streak.id,
            user_id=streak.user_id,
            current_streak=streak.current_streak,
            highest_streak=streak.highest_streak,
            last_claim_date=streak.last_claim_date,
            kyc_eligible=kyc_eligible,
            star_coupon_tier=coupon_tier,
        )

    @staticmethod
    async def claim_daily_streak(db: Session, user: User) -> ClaimStreakResponse:
        streak = db.query(Streak).filter(Streak.user_id == user.id).first()

        if not streak:
            streak = Streak(
                user_id=user.id,
                current_streak=0,
                highest_streak=0,
                last_claim_date=None,
            )
            db.add(streak)

        today = date.today()

        if streak.last_claim_date == today:
            referral_count = db.query(Referral).filter(Referral.referrer_id == user.id).count()
            coupon_tier = StreakService.calculate_coupon_tier(streak.current_streak, referral_count)
            return ClaimStreakResponse(
                message="Streak already claimed for today.",
                current_streak=streak.current_streak,
                highest_streak=streak.highest_streak,
                claimed_today=True,
                coupon_unlocked=coupon_tier,
            )

        if streak.last_claim_date == today - timedelta(days=1):
            streak.current_streak += 1
        else:
            streak.current_streak = 1

        streak.highest_streak = max(streak.highest_streak, streak.current_streak)
        streak.last_claim_date = today

        db.commit()
        db.refresh(streak)

        referral_count = db.query(Referral).filter(Referral.referrer_id == user.id).count()
        coupon_tier = StreakService.calculate_coupon_tier(streak.current_streak, referral_count)

        return ClaimStreakResponse(
            message="Daily streak claimed successfully!",
            current_streak=streak.current_streak,
            highest_streak=streak.highest_streak,
            claimed_today=True,
            coupon_unlocked=coupon_tier,
        )
