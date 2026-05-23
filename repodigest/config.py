"""Configuration loading and validation for repodigest."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

import yaml

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.repodigest.yml")
DEFAULT_DAYS = 7
DEFAULT_OUTPUT_FORMAT = "text"
VALID_FORMATS = {"text", "markdown", "json"}


@dataclass
class Config:
    token: str = ""
    repo: str = ""
    days: int = DEFAULT_DAYS
    output_format: str = DEFAULT_OUTPUT_FORMAT
    output_file: Optional[str] = None
    cache_ttl: int = 300
    extra_labels: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        """Return a list of validation error messages (empty if valid)."""
        errors: list[str] = []
        if not self.token:
            errors.append("GitHub token is required (set GITHUB_TOKEN or 'token' in config).")
        if not self.repo or "/" not in self.repo:
            errors.append("'repo' must be in 'owner/name' format.")
        if self.days < 1 or self.days > 365:
            errors.append("'days' must be between 1 and 365.")
        if self.output_format not in VALID_FORMATS:
            errors.append(f"'output_format' must be one of {sorted(VALID_FORMATS)}.")
        if self.cache_ttl < 0:
            errors.append("'cache_ttl' must be >= 0.")
        return errors


def load_config(path: str = DEFAULT_CONFIG_PATH, overrides: Optional[dict] = None) -> Config:
    """Load config from a YAML file, then apply env vars and explicit overrides."""
    data: dict = {}

    if os.path.exists(path):
        with open(path, "r") as fh:
            data = yaml.safe_load(fh) or {}

    # Environment variable overrides
    if os.environ.get("GITHUB_TOKEN"):
        data["token"] = os.environ["GITHUB_TOKEN"]
    if os.environ.get("REPODIGEST_REPO"):
        data["repo"] = os.environ["REPODIGEST_REPO"]
    if os.environ.get("REPODIGEST_DAYS"):
        data["days"] = int(os.environ["REPODIGEST_DAYS"])
    if os.environ.get("REPODIGEST_FORMAT"):
        data["output_format"] = os.environ["REPODIGEST_FORMAT"]

    if overrides:
        data.update({k: v for k, v in overrides.items() if v is not None})

    return Config(
        token=data.get("token", ""),
        repo=data.get("repo", ""),
        days=int(data.get("days", DEFAULT_DAYS)),
        output_format=data.get("output_format", DEFAULT_OUTPUT_FORMAT),
        output_file=data.get("output_file"),
        cache_ttl=int(data.get("cache_ttl", 300)),
        extra_labels=list(data.get("extra_labels", [])),
    )
