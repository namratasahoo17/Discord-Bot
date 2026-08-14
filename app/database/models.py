from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .connection import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

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