from datetime import date
from uuid import uuid4

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DailyUsage(Base):
    __tablename__ = "daily_usage"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    usage_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    banner_ads: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    interstitial_ads: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    rewarded_ads: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    native_ads: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    user = relationship(
        "User",
        back_populates="daily_usage"
    )