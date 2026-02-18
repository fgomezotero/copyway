import os
import yaml
from pathlib import Path
from .exceptions import ConfigError


class Config:
    def __init__(self, config_file=None):
        self.config_file = config_file or os.getenv("COPYWAY_CONFIG", str(Path.home() / ".copyway.yml"))
        self.data = self._load()

    def _load(self):
        path = Path(self.config_file)
        if not path.exists():
            return {}
        try:
            with open(path) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise ConfigError(f"Error cargando configuración: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def get_protocol_config(self, protocol):
        return self.data.get("protocols", {}).get(protocol, {})
