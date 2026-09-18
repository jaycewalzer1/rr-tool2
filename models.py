"""SQLAlchemy models for users and their uploaded documents."""

from __future__ import annotations

from datetime import UTC, datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base so models get full static typing support.

    Models subclass ``Base`` rather than ``db.Model``: Flask-SQLAlchemy builds
    ``db.Model`` dynamically, which type checkers cannot follow, and registers
    ``Base`` subclasses on the same metadata either way.
    """


db = SQLAlchemy(model_class=Base)


def _utcnow() -> datetime:
    return datetime.now(UTC)


class User(Base):
    """A subscriber, mirrored from the AWS Cognito user pool."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cognito_sub: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(15))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100), unique=True, default=None)
    subscription_status: Mapped[str] = mapped_column(String(20), default="inactive")
    subscription_end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    files: Mapped[list[File]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class File(Base):
    """A rent roll PDF uploaded by a user and stored in S3."""

    __tablename__ = "file"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    upload_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    s3_key: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str | None] = mapped_column(String(50), default=None)
    content_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)

    user: Mapped[User] = relationship(back_populates="files")

    def __repr__(self) -> str:
        return f"<File {self.filename} user_id={self.user_id}>"
