from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RedemptionCreate(BaseModel):
    coins: int = Field(..., ge=1000, description="Minimum 1000 coins to redeem")
    upi_id: Optional[str] = None
    note: Optional[str] = None


class RedemptionResponse(BaseModel):
    id: str
    coins: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RedemptionListResponse(BaseModel):
    items: list[RedemptionResponse]
    total: int
