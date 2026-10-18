"""Shared data models used across RDRS."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import PurePath


class EventType(str, Enum):
    CREATED = "created"
    MODIFIED = "modified"
    RENAMED = "renamed"
    DELETED = "deleted"


@dataclass(frozen=True)
class FileEvent:
    """One file-system change, in RDRS's own simple format."""

    event_type: EventType
    path: str
    timestamp: float = field(default_factory=time.time)
    dest_path: str | None = None  # new path, only for renames

    @property
    def extension(self) -> str:
        """Lower-case extension of the (new) path, e.g. '.locked'."""
        return PurePath(self.dest_path or self.path).suffix.lower()

    @property
    def old_extension(self) -> str:
        return PurePath(self.path).suffix.lower()

    @property
    def extension_changed(self) -> bool:
        """True for a rename that changed the extension (.docx -> .locked)."""
        return (
            self.event_type is EventType.RENAMED
            and self.dest_path is not None
            and self.extension != self.old_extension
        )

    