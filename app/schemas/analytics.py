from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnalyticsEventCreate(BaseModel):
    game_id: Optional[str] = None
    screen_time: Optional[float] = None  # seconds spent on screen
    duration: Optional[float] = None     # total session duration in seconds
    city: Optional[str] = None
    state: Optional[str] = None


class AnalyticsEventResponse(BaseModel):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
