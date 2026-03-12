import logging
import os
import pathlib
import time

from .workspace import get_cache_path

_logger = logging.getLogger(__name__)


def _get_path_for_key(name: str) -> pathlib.Path:
    cache_path = get_cache_path()
    return cache_path / name


def _get_content_age(key: str) -> float | None:
    file_path = _get_path_for_key(key)
    if file_path.exists():
        mod_time = file_path.stat().st_mtime
        age = time.time() - mod_time
        if age < 0:
            _logger.warning("Modification time is in the future!")
        return age
    else:
        return None


def update_cache(key: str, data: str) -> None:
    path = _get_path_for_key(key)
    _logger.debug(f"Cache key '{key}' age: {_get_content_age(key):.0f}s")
    with open(path, "r+") as file:
        prev_contents = file.read()
        if prev_contents == data:
            _logger.debug(f"Cache key '{key}' already up to date")
            # touch the file to extend the lifetime
            path.touch()
            return
        _logger.debug(f"Updating cache key: '{key}'")
        file.seek(0, os.SEEK_SET)
        file.write(data)
        file.truncate()


def get_cache_data(key: str, max_age_s: float | None = False) -> str | None:
    assert max_age_s is None or max_age_s > 0, "Max age must be positive."
    age = _get_content_age(key)
    if age is None:
        _logger.debug(f"Cache key not available '{key}'")
        return None
    if max_age_s is not None and age > max_age_s:
        _logger.debug(
            f"Cache key contents too old: '{key}'.\n"
            f"(age: {age:.0f}s, requested max: {max_age_s:.0f}s)"
        )
        return None
    path = _get_path_for_key(key)
    if path.exists():
        _logger.debug(f"Cache hit on key '{key}' (age: {age:.0f}s).")
        with open(path, "r") as file:
            return file.read()
    else:
        return None
