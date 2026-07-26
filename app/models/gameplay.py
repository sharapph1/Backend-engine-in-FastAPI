from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GamePlay(Base):
    __tablename__ = "gameplays"

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

    played_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="gameplays"
    )

    game = relationship(
        "Game",
        back_populates="gameplays"
    )