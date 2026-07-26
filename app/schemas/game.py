from datetime import datetime
from pydantic import BaseModel, HttpUrl


class GameCreate(BaseModel):
    title: str
    url: str


class GameResponse(BaseModel):
    id: str
    title: str
    url: str
    likes_count: int = 0
    pins_count: int = 0
    plays_count: int = 0
    is_liked: bool = False
    is_pinned: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class GameActionResponse(BaseModel):
    message: str
    active: bool
