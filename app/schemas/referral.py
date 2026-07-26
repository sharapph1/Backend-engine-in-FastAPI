from datetime import datetime
from pydantic import BaseModel


class ReferralClaimRequest(BaseModel):
    referral_code: str


class ReferralUser(BaseModel):
    id: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReferralResponse(BaseModel):
    id: str
    referrer_id: str
    referred_user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReferralStatsResponse(BaseModel):
    referral_code: str
    total_referrals: int
    referred_users: list[ReferralUser]
