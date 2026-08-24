from datetime import datetime, date

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    Date,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .connection import Base


# ============================================================
# USER
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    discord_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    college_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    # One user -> many study submissions
    submissions: Mapped[list["StudySubmission"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # One user -> many awarded badges
    user_badges: Mapped[list["UserBadge"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # One user -> many streak records
    streaks: Mapped[list["UserStreak"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


# ============================================================
# STUDY SUBMISSION
# ============================================================

class StudySubmission(Base):
    __tablename__ = "study_submissions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # Connect submission to User
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    # The date the study belongs to
    study_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    subject: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )

    # Connect submission back to User
    user: Mapped["User"] = relationship(
        back_populates="submissions"
    )

    # One study submission per user per day
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "study_date",
            name="unique_user_study_date",
        ),
    )


# ============================================================
# BADGE CATEGORY
# ============================================================

class BadgeCategory(Base):
    __tablename__ = "badge_categories"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    badges: Mapped[list["Badge"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )


# ============================================================
# BADGE
# ============================================================

class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("badge_categories.id"),
        nullable=False,
    )

    category: Mapped["BadgeCategory"] = relationship(
        back_populates="badges"
    )

    # Machine-readable badge requirement
    #
    # Examples:
    # "study_sessions_completed"
    # "consecutive_days_studied"
    # "subjects_studied"
    # "badges_earned"
    # "comeback"
    #
    # The actual badge-awarding logic will be implemented later.
    requirement_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    requirement_value: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    emoji: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    rarity: Mapped[str] = mapped_column(
        String(20),
        default="common",
        nullable=False,
    )

    # One badge -> many UserBadge records
    user_badges: Mapped[list["UserBadge"]] = relationship(
        back_populates="badge",
        cascade="all, delete-orphan",
    )


# ============================================================
# USER BADGE
# ============================================================

class UserBadge(Base):
    __tablename__ = "user_badges"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    badge_id: Mapped[int] = mapped_column(
        ForeignKey("badges.id"),
        nullable=False,
    )

    awarded_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )

    # Optional custom icon
    icon: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Connect back to User
    user: Mapped["User"] = relationship(
        back_populates="user_badges"
    )

    # Connect back to Badge
    badge: Mapped["Badge"] = relationship(
        back_populates="user_badges"
    )

    # A user cannot receive the exact same badge twice
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "badge_id",
            name="unique_user_badge",
        ),
    )


# ============================================================
# USER STREAK
# ============================================================

class UserStreak(Base):
    __tablename__ = "user_streaks"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    length: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="streaks"
    )