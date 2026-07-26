from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GamePin(Base):
    __tablename__ = "gamepins"

    __table_args__ = (
        UniqueConstraint("user_id", "game_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    game_id: Mapped[str] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="pins"
    )

    game = relationship(
        "Game",
        back_populates="pins"
    )