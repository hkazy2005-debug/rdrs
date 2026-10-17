"""RDRS entry point. Day 2: config + logging working together."""
from __future__ import annotations

from app.core.config import load_settings
from app.core.logging_setup import get_logger, setup_logging


def main() -> None:
    settings = load_settings()
    setup_logging(settings.logging)
    log = get_logger("system")
    log.info("RDRS started | simulation_mode={}", settings.response.simulation_mode)
    log.info("Watching folders: {}", settings.watch.folders)


if __name__ == "__main__":
    main()

    