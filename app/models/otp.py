from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Integer, Boolean
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OTP(Base):
    __tablename__ = "otps"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    otp_hash: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    purpose: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.utcnow() + timedelta(minutes=5)
    )

    user = relationship(
        "User",
        back_populates="otps"
    )

    attempts: Mapped[int] = mapped_column(
    Integer,
    default=0,
    nullable=False
    )

    is_used: Mapped[bool] = mapped_column(
    Boolean,
    default=False,
    nullable=False
)