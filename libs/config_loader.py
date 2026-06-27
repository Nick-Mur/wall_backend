from pathlib import Path
from typing import Any
import json
import os


class ConfigLoader:
    def __init__(self, config_path: str | None = None, env_prefix: str = "") -> None:
        self.config_path = Path(config_path or "config.json")
        if env_prefix:
            self.env_prefix = env_prefix.strip("_") + "__"
        else:
            self.env_prefix = ""

    def load(self) -> dict[str, Any]:
        config = self.read_config_file()

        for key, value in os.environ.items():
            if not key.startswith(self.env_prefix):
                continue

            parts = self.format_env_key(key)
            if not parts:
                continue

            self.set_nested(config, parts, self.cast_type(value))

        return config

    def read_config_file(self) -> dict[str, Any]:
        if not self.config_path.exists():
            return {}

        try:
            with self.config_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return {}

        return data if isinstance(data, dict) else {}

    def format_env_key(self, key: str) -> list[str]:
        if self.env_prefix:
            s = key[len(self.env_prefix):]
        else:
            s = key
        return [part.lower().strip() for part in s.split("__") if part.strip()]

    # если словари вложены друг в друга
    def set_nested(self, target: dict[str, Any], path: list[str], value: Any) -> None:
        current = target
        for part in path[:-1]:
            if not isinstance(current.get(part), dict):
                current[part] = {}
            current = current[part]
        current[path[-1]] = value

    def cast_type(self, value: str) -> Any:
        stripped = value.strip()
        lowered = stripped.lower()

        # тут пробуем привести к булевым
        if lowered in {"true", "false"}:
            return lowered == "true"
        if lowered in {"null", "none"}:
            return None

        # тут пробуем массивы или объекты
        if stripped.startswith("[") or stripped.startswith("{"):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                pass

        # тут пробуем числа
        try:
            return int(stripped)
        except ValueError:
            try:
                return float(stripped)
            except ValueError:
                return value


def load_config(config_path: str | None = None, env_prefix: str = "") -> dict[str, Any]:
    return ConfigLoader(config_path=config_path, env_prefix=env_prefix).load()
