"""Structured logging configuration for openclaw-mcp."""

import json
import logging
import logging.handlers
import sys
from datetime import UTC, datetime
from pathlib import Path

from openclaw_mcp.config import Settings


def _structured_record(record: logging.LogRecord) -> str:
    """Format a log record as a single-line JSON object for file output."""
    payload: dict = {
        "ts": datetime.now(UTC).isoformat(),
        "level": record.levelname,
        "logger": record.name,
        "msg": record.getMessage(),
    }
    if record.exc_info:
        payload["exc"] = record.exc_info[1].__class__.__name__ if record.exc_info[1] else None
    if hasattr(record, "tool"):
        payload["tool"] = record.tool
    if hasattr(record, "operation"):
        payload["operation"] = record.operation
    if hasattr(record, "error_type"):
        payload["error_type"] = record.error_type
    return json.dumps(payload, default=str) + "\n"


class StructuredFileFormatter(logging.Formatter):
    """Formatter that emits one JSON object per line for file handler."""

    def format(self, record: logging.LogRecord) -> str:
        return _structured_record(record).rstrip()


class StructuredStreamFormatter(logging.Formatter):
    """Human-readable format for stderr with optional extra fields."""

    def format(self, record: logging.LogRecord) -> str:
        base = f"{self.formatTime(record)} [{record.levelname}] {record.name}: {record.getMessage()}"
        if hasattr(record, "tool"):
            base += f" tool={record.tool}"
        if hasattr(record, "operation"):
            base += f" operation={record.operation}"
        if record.exc_info:
            base += f" exc={record.exc_info[1]!r}"
        return base


def setup_logging(settings: Settings | None = None) -> None:
    """Configure structured logging: stderr + rotating file in log_dir."""
    settings = settings or Settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "openclaw-mcp.log"

    root = logging.getLogger()
    root.setLevel(level)
    for h in list(root.handlers):
        root.removeHandler(h)

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(StructuredStreamFormatter())
    root.addHandler(stream_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(StructuredFileFormatter())
    root.addHandler(file_handler)

    root.info(
        "Logging configured",
        extra={"tool": "openclaw_mcp", "operation": "startup", "log_file": str(log_file)},
    )


def get_log_file_path(settings: Settings | None = None) -> Path:
    """Return the path to the current log file (for log server)."""
    settings = settings or Settings()
    return Path(settings.log_dir) / "openclaw-mcp.log"
