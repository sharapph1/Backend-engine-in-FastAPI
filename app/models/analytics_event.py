from datetime import datetime
from uuid import uuid4
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Duration the user spent on a game/screen (in seconds)
    screen_time: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    game_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("games.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Total session duration in seconds
    duration: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    state: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="analytics_events"
    )
