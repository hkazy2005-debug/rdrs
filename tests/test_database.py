from app.core.models import EventType, FileEvent
from app.database.db import Database
from app.database.models import AlertRow, IncidentRow, ProcessRow, ScoreRow


def make_db(tmp_path):
    return Database(f"sqlite:///{tmp_path / 'test.db'}")


def test_tables_are_created(tmp_path):
    db = make_db(tmp_path)
    names = set(db.engine.dialect.get_table_names(db.engine.connect()))
    assert {"events", "processes", "scores", "alerts", "incidents"} <= names


def test_add_and_read_event(tmp_path):
    db = make_db(tmp_path)
    db.add_event(FileEvent(EventType.RENAMED, "/s/a.txt", dest_path="/s/a.locked"))
    assert db.count_events() == 1
    row = db.recent_events()[0]
    assert row.event_type == "renamed"
    assert row.dest_path == "/s/a.locked"
    assert row.extension == ".locked"


def test_recent_events_newest_first_and_limited(tmp_path):
    db = make_db(tmp_path)
    for i in range(5):
        db.add_event(FileEvent(EventType.CREATED, f"/s/f{i}.txt"))
    rows = db.recent_events(limit=3)
    assert [r.path for r in rows] == ["/s/f4.txt", "/s/f3.txt", "/s/f2.txt"]


def test_other_tables_accept_rows(tmp_path):
    db = make_db(tmp_path)
    with db.session() as s:
        s.add(ProcessRow(pid=1, name="python", timestamp=1.0))
        s.add(ScoreRow(timestamp=1.0, score=80, level="critical", reasons="burst"))
        inc = IncidentRow(score=80, level="critical", suspect_process="python")
        s.add(inc)
        s.flush()
        s.add(AlertRow(level="critical", message="test", incident_id=inc.id))
        s.commit()
        assert s.get(IncidentRow, inc.id).status == "open"

        