"""Configure application logging for the desktop editor."""

from __future__ import annotations

import logging
import logging.config
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.config.path_handler import LOGS_DIR

MAX_LOG_BYTES = 1_000_000
LOG_BACKUP_COUNT = 3
ROOT_LOG_LEVEL = "DEBUG"
FILE_LOG_LEVEL = "DEBUG"
CONSOLE_LOG_LEVEL = "INFO"
EST = timezone(timedelta(hours=-5), name="EST")


class EstFormatter(logging.Formatter):
    """Format log-record timestamps in fixed EST."""

    def formatTime(
        self,
        record: logging.LogRecord,
        datefmt: str | None = None,
    ) -> str:
        """Render log-record time in fixed EST.

        - Uses ``datefmt`` when one is given.
        - Otherwise returns an ISO 8601 timestamp to the minute.
        - The offset is always UTC-5; daylight saving time is not applied.
        """
        dt = datetime.fromtimestamp(record.created, tz=EST)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat(timespec="minutes")


def _rotating_handler_factory(filename: str) -> RotatingFileHandler:
    """Create a rotating file handler with shared sizing and naming rules.

    - Rotates at ``MAX_LOG_BYTES`` and keeps ``LOG_BACKUP_COUNT`` backups.
    - Names backups ``<stem>.<n>.log`` instead of the default ``<name>.<n>``
      so rotated files keep the ``.log`` extension.
    """
    handler = RotatingFileHandler(
        filename=filename,
        maxBytes=MAX_LOG_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    source_path = Path(filename)

    def _rotated_log_namer(default_name: str) -> str:
        rotated_path = Path(default_name)
        rotation_suffix = rotated_path.suffix.lstrip(".")
        base_stem = source_path.stem
        base_stem = base_stem.removesuffix(".log")
        return str(rotated_path.with_name(f"{base_stem}.{rotation_suffix}.log"))

    handler.namer = _rotated_log_namer
    return handler


def configure_logging(project_name: str | None = None) -> None:
    """Configure root logging to a rotating file and the console.

    - Creates ``LOGS_DIR`` when it does not exist.
    - Names the log file after ``project_name``, or after the folder that
      contains ``LOGS_DIR`` when no name is given; spaces become underscores.
    - The file handler records DEBUG and above; the console shows INFO and
      above.
    - Existing loggers stay enabled.
    """
    logs_dir = LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not project_name:
        project_name = logs_dir.parent.name
    safe_project_name = project_name.replace(" ", "_")

    config: dict[str, object] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "file_detail": {
                "()": EstFormatter,
                "format": "%(asctime)s %(levelname)s %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %I:%M%p",
            },
            "console_minimal": {
                "format": "%(message)s",
            },
        },
        "handlers": {
            "app_file": {
                "()": _rotating_handler_factory,
                "filename": str(logs_dir / f"{safe_project_name}.log"),
                "formatter": "file_detail",
                "level": FILE_LOG_LEVEL,
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console_minimal",
                "level": CONSOLE_LOG_LEVEL,
            },
        },
        "root": {
            "level": ROOT_LOG_LEVEL,
            "handlers": ["app_file", "console"],
        },
    }
    logging.config.dictConfig(config)
