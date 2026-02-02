"""Configuration for openclaw-mcp."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """openclaw-mcp settings."""

    model_config = SettingsConfigDict(
        env_prefix="OPENCLAW_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    gateway_url: str = Field(
        default="http://127.0.0.1:18789",
        description="OpenClaw Gateway HTTP base URL",
    )
    gateway_token: str | None = Field(
        default=None,
        description="Bearer token for Tools Invoke and Webhooks",
    )
    moltbook_api_key: str | None = Field(
        default=None,
        description="Moltbook agent API key (env: MOLTBOOK_API_KEY or OPENCLAW_MOLTBOOK_API_KEY)",
    )
    moltbook_url: str = Field(
        default="https://www.moltbook.com/api/v1",
        description="Moltbook API base URL (use www to preserve Authorization header)",
    )
    openclaw_path: str = Field(
        default="openclaw",
        description="Path to openclaw CLI binary",
    )
    workspace_path: Path | None = Field(
        default=None,
        description="OpenClaw workspace root (default: ~/.openclaw/workspace)",
    )
    log_dir: Path = Field(
        default_factory=lambda: Path.home() / ".openclaw-mcp" / "logs",
        description="Log directory. Set OPENCLAW_LOG_DIR to override.",
    )
    log_level: str = Field(
        default="INFO",
        description="Log level: DEBUG, INFO, WARNING, ERROR",
    )
    log_max_bytes: int = Field(
        default=2 * 1024 * 1024,
        description="Max bytes per log file (rotating)",
    )
    log_backup_count: int = Field(
        default=3,
        description="Number of backup log files to keep",
    )
