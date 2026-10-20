import time

from watchdog.events import (
    DirCreatedEvent,
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
)

from app.core.models import EventType, FileEvent
from app.detectors.monitor import FileMonitor, _Handler


def test_handler_translates_all_four_event_types():
    got: list[FileEvent] = []
    h = _Handler(got.append)
    h.on_any_event(FileCreatedEvent("/s/a.txt"))
    h.on_any_event(FileModifiedEvent("/s/a.txt"))
    h.on_any_event(FileMovedEvent("/s/a.txt", "/s/a.locked"))
    h.on_any_event(FileDeletedEvent("/s/a.locked"))
    assert [e.event_type for e in got] == [
        EventType.CREATED, EventType.MODIFIED, EventType.RENAMED, EventType.DELETED,
    ]
    assert got[2].dest_path == "/s/a.locked"


def test_handler_ignores_directories():
    got: list[FileEvent] = []
    _Handler(got.append).on_any_event(DirCreatedEvent("/s/folder"))
    assert got == []


def test_extension_helpers():
    e = FileEvent(EventType.RENAMED, "/s/report.DOCX", dest_path="/s/report.locked")
    assert e.extension == ".locked"
    assert e.old_extension == ".docx"
    assert e.extension_changed
    assert not FileEvent(EventType.CREATED, "/s/x.txt").extension_changed


def _wait(cond, timeout=5.0):
    end = time.time() + timeout
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.05)
    return False


def test_live_monitor_sees_real_file_changes(tmp_path):
    seen: list[FileEvent] = []
    mon = FileMonitor([str(tmp_path)], on_event=seen.append)
    mon.start()
    try:
        f = tmp_path / "doc.txt"
        f.write_text("hello")
        f.rename(tmp_path / "doc.locked")
        (tmp_path / "doc.locked").unlink()
        assert _wait(lambda: mon.counts["deleted"] >= 1)
    finally:
        mon.stop()
    c = mon.counts
    assert c["created"] >= 1 and c["renamed"] == 1 and c["deleted"] == 1
    assert mon.total == sum(c.values())
    assert any(e.extension_changed for e in seen)


def test_bad_callback_does_not_stop_monitoring(tmp_path):
    mon = FileMonitor([str(tmp_path)], on_event=lambda e: 1 / 0)
    ok: list[FileEvent] = []
    mon.subscribe(ok.append)
    mon.start()
    try:
        (tmp_path / "a.txt").write_text("x")
        assert _wait(lambda: len(ok) > 0)
    finally:
        mon.stop()

        

        