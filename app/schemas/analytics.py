from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AnalyticsEventCreate(BaseModel):
    game_id: Optional[str] = None
    screen_time: Optional[float] = None  # seconds on screen
    duration: Optional[float] = None     # session duration seconds
    city: Optional[str] = None
    state: Optional[str] = None
    event_type: Optional[str] = None     # e.g. 'game_open', 'game_close', 'screen_view'


class AnalyticsEventResponse(BaseModel):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
