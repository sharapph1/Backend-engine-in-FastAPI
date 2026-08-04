from typing import Optional
from pydantic import BaseModel, Field


class UpdateUsernameRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")


class UpdateReferIdRequest(BaseModel):
    refer_id: str = Field(..., min_length=4, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")


class ProfileUpdateResponse(BaseModel):
    """Returned after any successful profile field update."""
    message: str
    username: Optional[str] = None
    refer_id: Optional[str] = None
    avatar_url: Optional[str] = None
