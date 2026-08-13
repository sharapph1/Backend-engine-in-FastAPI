from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    username: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    refer_id: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    last_login: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # Relationships

    otps = relationship(
        "OTP",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    sessions = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    streak = relationship(
        "Streak",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    referrals_sent = relationship(
        "Referral",
        foreign_keys="Referral.referrer_id",
        back_populates="referrer"
    )

    referrals_received = relationship(
        "Referral",
        foreign_keys="Referral.referred_user_id",
        back_populates="referred"
    )

    daily_usage = relationship(
        "DailyUsage",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    wallet = relationship(
        "UserWallet",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    redemptions = relationship(
        "Redemption",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    analytics_events = relationship(
        "AnalyticsEvent",
        back_populates="user",
        cascade="all, delete-orphan"
    )