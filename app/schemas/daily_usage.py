from datetime import date
from pydantic import BaseModel


class AdImpressionLog(BaseModel):
    ad_type: str  # "banner", "interstitial", "rewarded", "native"
    count: int = 1


class DailyUsageResponse(BaseModel):
    id: str
    user_id: str
    usage_date: date
    banner_ads: int
    interstitial_ads: int
    rewarded_ads: int
    native_ads: int

    class Config:
        from_attributes = True
