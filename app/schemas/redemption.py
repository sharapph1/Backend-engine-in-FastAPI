from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RedemptionCreate(BaseModel):
    coins: int = Field(..., ge=1000, description="Minimum 1000 coins to redeem")
    upi_id: str = Field(..., min_length=3, description="UPI ID is required (e.g. user@upi)")
    full_name: str = Field(..., min_length=1, description="Account holder full name")


class RedemptionResponse(BaseModel):
    id: str
    coins: int
    upi_id: str
    full_name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RedemptionListResponse(BaseModel):
    items: list[RedemptionResponse]
    total: int
