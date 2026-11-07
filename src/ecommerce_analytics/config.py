"""
Configuration Management Module
-------------------------------
Loads configurations using pathlib for cross-platform compatibility (Windows/Linux/macOS).
"""

from pathlib import Path
import yaml
from typing import Dict, Any

# Root directory of the project (2 levels up from src/ecommerce_analytics)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class ConfigManager:
    """Manages project paths and configuration settings dynamically."""

    def __init__(self, config_file: str = "config/config.yaml") -> None:
        self.config_path = PROJECT_ROOT / config_file
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Reads configuration file cleanly without hardcoded paths."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found at: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def get_path(self, key: str) -> Path:
        """Retrieves absolute path for a defined folder in configuration."""
        relative_path = self._config["paths"].get(key)
        if not relative_path:
            raise KeyError(f"Path key '{key}' not found in configuration.")
        return PROJECT_ROOT / relative_path

    @property
    def business_rules(self) -> Dict[str, Any]:
        """Returns key business metrics and rules."""
        return self._config.get("business_rules", {})

if __name__ == "__main__":
    # Internal Verification Check
    config = ConfigManager()
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Raw Data Path: {config.get_path('raw_data')}")
    print("Configuration loaded successfully.")