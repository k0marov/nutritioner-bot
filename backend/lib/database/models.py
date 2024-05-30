"""File with model for database."""
from datetime import date, datetime
import uuid

from sqlalchemy import Date, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for models."""

    pass


class Meal(Base):
    """Class with model for database."""

    __tablename__ = 'meal'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    calories: Mapped[float]
    created_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now().date())
