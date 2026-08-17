from datetime import datetime, date

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    Date,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .connection import Base


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
    )

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


class StudySubmission(Base):
    __tablename__ = "study_submissions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # Connect this submission to the User who made it
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    # The day this study belongs to.
    #
    # study_date = date being logged
    # created_at = exact time the submission was created
    #
    # Streaks should be based on study_date.
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
    )

    # Connect this submission back to its User
    user: Mapped["User"] = relationship(
        back_populates="submissions"
    )

    # A user can submit only ONE study log per day.
    #
    # This prevents multiple submissions on the same day
    # from manipulating study-day statistics.
    """__table_args__ = (
        UniqueConstraint(
            "user_id",
            "study_date",
            name="unique_user_study_date",
        ),
    )"""


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
    )

    # Connect this UserBadge back to the User
    user: Mapped["User"] = relationship(
        back_populates="user_badges"
    )

    # Connect this UserBadge to the Badge
    badge: Mapped["Badge"] = relationship()

    # A user should never receive the exact same badge twice.
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "badge_id",
            name="unique_user_badge",
        ),
    )