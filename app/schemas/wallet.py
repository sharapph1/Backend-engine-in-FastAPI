from datetime import datetime
from pydantic import BaseModel


class WalletResponse(BaseModel):
    user_id: str
    coins: int
    updated_at: datetime

    class Config:
        from_attributes = True
