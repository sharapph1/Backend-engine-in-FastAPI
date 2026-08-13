from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RedemptionCreate(BaseModel):
    coins: int = Field(..., ge=1000)  # minimum 1000 coins
    upi_id: str
    full_name: str
    note: Optional[str] = None


class RedemptionResponse(BaseModel):
    id: str
    coins: int
    status: str
    upi_id: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class RedemptionListResponse(BaseModel):
    items: list[RedemptionResponse]
    total: int
