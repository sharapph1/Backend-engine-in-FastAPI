from datetime import date
from uuid import uuid4

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Streak(Base):
    __tablename__ = "streaks"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    highest_streak: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    last_claim_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="streak"
    )