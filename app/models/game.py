from datetime import datetime
from uuid import uuid4
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    url: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    # isPrimary from schema — marks the featured/hero game
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_latest: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    thumbnail_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    plays_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # added_at kept for backward compat; updated_at matches schema image
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
