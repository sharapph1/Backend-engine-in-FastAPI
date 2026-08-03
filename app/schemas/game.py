from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GameCreate(BaseModel):
    title: str
    url: str
    thumbnail_url: Optional[str] = None
    is_latest: bool = False


class GameResponse(BaseModel):
    id: str
    title: str
    url: str
    thumbnail_url: Optional[str] = None
    is_latest: bool = False
    likes_count: int = 0
    plays_count: int = 0
    is_liked: bool = False
    added_at: datetime

    class Config:
        from_attributes = True


class GameActionResponse(BaseModel):
    message: str
    active: bool
