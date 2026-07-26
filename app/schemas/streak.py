from datetime import date
from pydantic import BaseModel


class StreakResponse(BaseModel):
    id: str
    user_id: str
    current_streak: int
    highest_streak: int
    last_claim_date: date | None
    kyc_eligible: bool
    star_coupon_tier: str | None

    class Config:
        from_attributes = True


class ClaimStreakResponse(BaseModel):
    message: str
    current_streak: int
    highest_streak: int
    claimed_today: bool
    coupon_unlocked: str | None
