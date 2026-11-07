"""Configuration loading helpers."""

from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load YAML configuration and resolve configured paths from the project root."""
    config_path = Path(path).resolve()
    with config_path.open(encoding="utf-8") as file:
        config = yaml.safe_load(file)
    if not isinstance(config, dict):
        raise ValueError(f"Configuration must contain a YAML mapping: {config_path}")

    root = PROJECT_ROOT if config_path == DEFAULT_CONFIG_PATH.resolve() else config_path.parent.parent
    config["paths"] = {
        key: str((root / value).resolve()) for key, value in config.get("paths", {}).items()
    }
    return config
