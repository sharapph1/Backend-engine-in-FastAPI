from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.daily_usage import DailyUsage
from app.models.user import User
from app.schemas.daily_usage import AdImpressionLog, DailyUsageResponse


class DailyUsageService:

    @staticmethod
    async def log_ad_impression(
        db: Session, user: User, data: AdImpressionLog
    ) -> DailyUsageResponse:
        today = date.today()
        usage = db.query(DailyUsage).filter(
            DailyUsage.user_id == user.id, DailyUsage.usage_date == today
        ).first()

        if not usage:
            usage = DailyUsage(
                user_id=user.id,
                usage_date=today,
                banner_ads=0,
                interstitial_ads=0,
                rewarded_ads=0,
                native_ads=0,
            )
            db.add(usage)

        ad_type = data.ad_type.lower()
        if ad_type == "banner":
            usage.banner_ads += data.count
        elif ad_type == "interstitial":
            usage.interstitial_ads += data.count
        elif ad_type == "rewarded":
            usage.rewarded_ads += data.count
        elif ad_type == "native":
            usage.native_ads += data.count
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ad_type '{data.ad_type}'. Must be banner, interstitial, rewarded, or native.",
            )

        db.commit()
        db.refresh(usage)

        return DailyUsageResponse.model_validate(usage)

    @staticmethod
    async def get_daily_usage(db: Session, user: User) -> DailyUsageResponse:
        today = date.today()
        usage = db.query(DailyUsage).filter(
            DailyUsage.user_id == user.id, DailyUsage.usage_date == today
        ).first()

        if not usage:
            usage = DailyUsage(
                user_id=user.id,
                usage_date=today,
                banner_ads=0,
                interstitial_ads=0,
                rewarded_ads=0,
                native_ads=0,
            )
            db.add(usage)
            db.commit()
            db.refresh(usage)

        return DailyUsageResponse.model_validate(usage)
