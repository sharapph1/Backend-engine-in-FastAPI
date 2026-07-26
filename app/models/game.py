from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String
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

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    gameplays = relationship(
        "GamePlay",
        back_populates="game",
        cascade="all, delete-orphan"
    )

    likes = relationship(
        "GameLike",
        back_populates="game",
        cascade="all, delete-orphan"
    )

    pins = relationship(
        "GamePin",
        back_populates="game",
        cascade="all, delete-orphan"
    )