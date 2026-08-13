from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GameCreate(BaseModel):
    title: str
    url: str
    thumbnail_url: Optional[str] = None
    is_latest: bool = False
    is_primary: bool = False
    updated_at: Optional[datetime] = None


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
    is_primary: bool = False
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GameActionResponse(BaseModel):
    message: str
    active: bool
