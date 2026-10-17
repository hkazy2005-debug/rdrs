"""Typed configuration loaded from config.yaml."""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class WatchConfig(BaseModel):
    folders: list[str] = ["data/sandbox"]
    recursive: bool = True


class DetectionConfig(BaseModel):
    window_seconds: int = Field(60, gt=0)
    modified_per_minute: int = 30
    renames_per_minute: int = 20
    extension_changes: int = 15
    entropy_threshold: float = Field(7.5, ge=0, le=8)
    entropy_sample_bytes: int = 65536


class Weights(BaseModel):
    rapid_encryption: int = 40
    mass_rename: int = 30
    high_entropy: int = 25
    cpu_spike: int = 15
    unknown_program: int = 10


class Levels(BaseModel):
    warning: int = 40
    critical: int = 70


class ScoringConfig(BaseModel):
    weights: Weights = Weights()
    levels: Levels = Levels()


class ResponseConfig(BaseModel):
    simulation_mode: bool = True
    terminate_process: bool = False
    quarantine_dir: str = "data/quarantine"


class StorageConfig(BaseModel):
    database_url: str = "sqlite:///data/rdrs.db"


class LoggingConfig(BaseModel):
    directory: str = "logs"
    rotation: str = "5 MB"
    retention: str = "14 days"


class Settings(BaseModel):
    watch: WatchConfig = WatchConfig()
    detection: DetectionConfig = DetectionConfig()
    scoring: ScoringConfig = ScoringConfig()
    response: ResponseConfig = ResponseConfig()
    storage: StorageConfig = StorageConfig()
    logging: LoggingConfig = LoggingConfig()


def load_settings(path: str | Path = "config.yaml") -> Settings:
    """Load settings from YAML. A missing file falls back to safe defaults."""
    p = Path(path)
    if not p.exists():
        return Settings()
    with p.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    return Settings(**raw)
