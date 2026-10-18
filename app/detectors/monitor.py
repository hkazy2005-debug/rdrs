"""Real-time file monitoring built on watchdog."""
from __future__ import annotations

import threading
from collections import Counter
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from app.core.logging_setup import get_logger
from app.core.models import EventType, FileEvent

EventCallback = Callable[[FileEvent], None]
_log = get_logger("events")

_WATCHDOG_TO_RDRS = {
    "created": EventType.CREATED,
    "modified": EventType.MODIFIED,
    "moved": EventType.RENAMED,
    "deleted": EventType.DELETED,
}


class _Handler(FileSystemEventHandler):
    """Translates raw watchdog events into FileEvent objects."""

    def __init__(self, on_event: EventCallback) -> None:
        self._on_event = on_event

    def on_any_event(self, event: FileSystemEvent) -> None:
        kind = _WATCHDOG_TO_RDRS.get(event.event_type)
        if kind is None or event.is_directory:  # ignore other types + folders
            return
        dest = str(event.dest_path) if kind is EventType.RENAMED and event.dest_path else None
        self._on_event(FileEvent(kind, str(event.src_path), dest_path=dest))


class FileMonitor:
    """Watch folders and report every create/modify/rename/delete."""

    def __init__(
        self,
        folders: list[str],
        recursive: bool = True,
        on_event: EventCallback | None = None,
    ) -> None:
        self.folders = [Path(f) for f in folders]
        self.recursive = recursive
        self._callbacks: list[EventCallback] = [on_event] if on_event else []
        self._counts: Counter[str] = Counter()
        self._lock = threading.Lock()
        self._observer = Observer()
        self._running = False

    def subscribe(self, callback: EventCallback) -> None:
        """Register another consumer (detection engine, database, ...)."""
        self._callbacks.append(callback)

    def _dispatch(self, event: FileEvent) -> None:
        with self._lock:
            self._counts[event.event_type.value] += 1
        _log.info("{} {}{}", event.event_type.value, event.path,
                  f" -> {event.dest_path}" if event.dest_path else "")
        for cb in self._callbacks:
            try:
                cb(event)
            except Exception:  # one bad consumer must not stop monitoring
                _log.opt(exception=True).error("event callback failed")

    @property
    def counts(self) -> dict[str, int]:
        with self._lock:
            return {t.value: self._counts[t.value] for t in EventType}

    @property
    def total(self) -> int:
        with self._lock:
            return sum(self._counts.values())

    def start(self) -> None:
        if self._running:
            return
        handler = _Handler(self._dispatch)
        for folder in self.folders:
            folder.mkdir(parents=True, exist_ok=True)
            self._observer.schedule(handler, str(folder), recursive=self.recursive)
        self._observer.start()
        self._running = True

    def stop(self) -> None:
        if not self._running:
            return
        self._observer.stop()
        self._observer.join(timeout=5)
        self._running = False

        