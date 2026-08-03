from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    # New fields added per refactor
    thumbnail_url: Mapped[str | None] = mapped_column(String, nullable=True)
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    plays_count: Mapped[int] = mapped_column(Integer, default=0)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
