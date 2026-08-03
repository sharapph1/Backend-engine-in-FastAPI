from datetime import datetime
from pydantic import BaseModel


class GameCreate(BaseModel):
    title: str
    url: str
    thumbnail_url: str | None = None
    is_latest: bool = False
    added_at: datetime | None = None


class GameResponse(BaseModel):
    id: str
    title: str
    url: str
    thumbnail_url: str | None = None
    is_latest: bool = False
    likes_count: int = 0
    plays_count: int = 0
    is_liked: bool = False
    is_pinned: bool = False
    added_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class GameActionResponse(BaseModel):
    message: str
    active: bool
