import dataclasses
import functools
import json
import logging

from ..common.errors import UserError
from ..common.workspace import get_settings_file_path

_logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Settings:
    environment: dict[str, str] = dataclasses.field(default_factory=lambda: {})


@functools.cache
def get_settings() -> Settings:
    path = get_settings_file_path()
    if not path.exists():
        _logger.info(
            "No settings file found. Using defaults.\n"
            f"You can add config file at '{path}'"
        )
        return Settings()
    try:
        with open(path, "r") as file:
            json_data = json.load(file)
            _logger.debug(f"Loaded config: '{json_data}'")
            settings = Settings(**json_data)
    except Exception as e:
        _logger.error(
            f"Could not load settings from '{path}'. Reason:\n"
            f"{e.__class__.__name__}: {e}"
        )
        raise UserError("Failed to load settings")
    _logger.debug("Successfully loaded settings.")
    return settings
