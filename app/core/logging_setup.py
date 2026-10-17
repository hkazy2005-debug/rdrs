"""Rotating log files: system, events, alerts, errors and audit."""
from __future__ import annotations

from pathlib import Path

from loguru import logger

from app.core.config import LoggingConfig

CHANNELS = ("system", "events", "alerts", "errors", "audit")
_configured = False


def setup_logging(cfg: LoggingConfig | None = None) -> None:
    """Create one rotating file per channel. Safe to call more than once."""
    global _configured
    if _configured:
        return
    cfg = cfg or LoggingConfig()
    directory = Path(cfg.directory)
    directory.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(lambda m: print(m, end=""), level="INFO", colorize=False)
    for channel in CHANNELS:
        logger.add(
            directory / f"{channel}.log",
            rotation=cfg.rotation,
            retention=cfg.retention,
            level="ERROR" if channel == "errors" else "INFO",
            filter=(lambda r, c=channel: r["extra"].get("channel") == c)
            if channel != "errors"
            else None,
            enqueue=True,
        )
    _configured = True


def get_logger(channel: str = "system"):
    """Return a logger bound to one of the channels."""
    return logger.bind(channel=channel)

