"""RDRS entry point.

    python -m app.main                  # watch folders from config.yaml
    python -m app.main --watch ./data/sandbox
"""
from __future__ import annotations

import argparse
import sys
import time

from app.core.config import load_settings
from app.core.logging_setup import get_logger, setup_logging
from app.detectors.monitor import FileMonitor
from app.database.db import Database


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="RDRS - Ransomware Detection & Response System")
    ap.add_argument("--watch", action="append", help="folder to watch (repeatable)")
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args(argv)

    settings = load_settings(args.config)
    setup_logging(settings.logging)
    log = get_logger("system")

    folders = args.watch or settings.watch.folders
    db = Database(settings.storage.database_url)
    monitor = FileMonitor(folders, settings.watch.recursive)
    monitor.subscribe(db.add_event)
    monitor.start()
    log.info("RDRS started | simulation_mode={} | watching {}",
             settings.response.simulation_mode, folders)
    try:
        while True:
            c = monitor.counts
            sys.stdout.write(
                f"\rEvents: {monitor.total:>6} | created {c['created']} | modified "
                f"{c['modified']} | renamed {c['renamed']} | deleted {c['deleted']}   "
            )
            sys.stdout.flush()
            time.sleep(0.5)
    except KeyboardInterrupt:
        print()
        log.info("RDRS stopped")
    finally:
        monitor.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


