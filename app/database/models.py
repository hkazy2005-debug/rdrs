"""Database tables for RDRS (SQLAlchemy 2.0 style)."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class EventRow(Base):
    """One file event seen by the monitor."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(16), index=True)
    path: Mapped[str] = mapped_column(Text)
    dest_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    extension: Mapped[str] = mapped_column(String(32), default="")
    timestamp: Mapped[float] = mapped_column(Float, index=True)


class ProcessRow(Base):
    """A snapshot of one running process."""

    __tablename__ = "processes"

    id: Mapped[int] = mapped_column(primary_key=True)
    pid: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(255))
    cpu_percent: Mapped[float] = mapped_column(Float, default=0.0)
    memory_mb: Mapped[float] = mapped_column(Float, default=0.0)
    disk_write_bytes: Mapped[int] = mapped_column(Integer, default=0)
    exe: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_pid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[float] = mapped_column(Float, index=True)


class ScoreRow(Base):
    """A threat score calculated at one moment."""

    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[float] = mapped_column(Float, index=True)
    score: Mapped[int] = mapped_column(Integer)
    level: Mapped[str] = mapped_column(String(16))
    reasons: Mapped[str] = mapped_column(Text, default="")


class IncidentRow(Base):
    """A Critical situation that needs a report."""

    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    score: Mapped[int] = mapped_column(Integer)
    level: Mapped[str] = mapped_column(String(16))
    suspect_process: Mapped[str | None] = mapped_column(String(255), nullable=True)
    affected_files: Mapped[str] = mapped_column(Text, default="")
    evidence_dir: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="open")


class AlertRow(Base):
    """A message raised for the operator."""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    level: Mapped[str] = mapped_column(String(16), index=True)
    message: Mapped[str] = mapped_column(Text)
    incident_id: Mapped[int | None] = mapped_column(ForeignKey("incidents.id"), nullable=True)

    