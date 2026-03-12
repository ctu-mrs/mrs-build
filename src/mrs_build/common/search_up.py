import logging
import pathlib

_logger = logging.getLogger(__name__)


def search_up(path: pathlib.Path, suffix: str) -> pathlib.Path | None:
    path = path.resolve()
    assert path.exists()
    if path.is_file():
        dir = path.parent
    elif path.is_dir():
        dir = path
    else:
        msg = f"Could not start search at path: '{path}'"
        _logger.error(msg)
        raise RuntimeError(msg)
    while not (dir / suffix).exists():
        new_dir = dir.parent
        if new_dir == dir:
            # We reached filesystem root
            return None
        dir = new_dir
    return dir
