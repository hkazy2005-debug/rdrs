"""Database access: create tables, save events, read them back."""
from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.models import FileEvent
from app.database.models import Base, EventRow


class Database:
    """Small wrapper so the rest of RDRS never touches SQL directly."""

    def __init__(self, url: str = "sqlite:///data/rdrs.db") -> None:
        if url.startswith("sqlite:///") and ":memory:" not in url:
            Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(url)
        Base.metadata.create_all(self.engine)
        self._session_factory = sessionmaker(self.engine, expire_on_commit=False)

    def session(self) -> Session:
        return self._session_factory()

    def add_event(self, event: FileEvent) -> None:
        """Save one FileEvent. Used as a monitor subscriber."""
        with self.session() as s:
            s.add(EventRow(
                event_type=event.event_type.value,
                path=event.path,
                dest_path=event.dest_path,
                extension=event.extension,
                timestamp=event.timestamp,
            ))
            s.commit()

    def count_events(self) -> int:
        with self.session() as s:
            return s.scalar(select(func.count()).select_from(EventRow)) or 0

    def recent_events(self, limit: int = 20) -> list[EventRow]:
        with self.session() as s:
            q = select(EventRow).order_by(EventRow.id.desc()).limit(limit)
            return list(s.scalars(q))

        