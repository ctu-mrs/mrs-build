import functools
import logging
import pathlib

from .errors import UserError
from .search_up import search_up

_logger = logging.getLogger(__name__)


_MRS_BUILD_DATA_DIR_NAME = ".mrs_build"
_SETTINGS_FILE_NAME = "mrs-build.json"
_CACHE_DIR_NAME = ".cache"


@functools.cache
def _find_workspace_path_impl() -> pathlib.Path | None:
    _logger.debug("Searching for workspace path...")
    dir = pathlib.Path()
    workspace_dir = search_up(dir, _MRS_BUILD_DATA_DIR_NAME)
    return workspace_dir


def _initialize_workspace_unchecked(path: pathlib.Path):
    config_path = path / _MRS_BUILD_DATA_DIR_NAME
    # create the config directory
    config_path.mkdir()
    # add COLCON_IGNORE
    (config_path / "COLCON_IGNORE").touch()
    _logger.info(f"Initialized workspace at '{path.absolute()}'")
    _find_workspace_path_impl.cache_clear()


def initialize_workspace(path: pathlib.Path):
    if not path.is_dir():
        msg = (
            f"Cannot initialize workspace.\n"
            f"Path must be a directory:\n"
            f"'{path}'"
        )
        _logger.error(msg)
        raise UserError(msg)
    config_path = path / _MRS_BUILD_DATA_DIR_NAME
    if config_path.is_dir():
        _logger.info(
            "Workspace was already initialized.\n"
            "If you want to reinitialize this workspace, remove the config\n"
            "directory and try again:\n"
            f"'{config_path.absolute()}'"
        )
        return
    if config_path.exists():
        msg = (
            f"Cannot initialize workspace.\n"
            f"Config path already exists and is not a directory:\n"
            f"'{config_path.absolute()}'"
        )
        _logger.error(msg)
        raise UserError(msg)
    _initialize_workspace_unchecked(path)


def find_workspace_path() -> pathlib.Path | None:
    return _find_workspace_path_impl()


def get_workspace_path() -> pathlib.Path:
    path = find_workspace_path()
    if path is None:
        msg = "Not in workspace."
        _logger.error(msg)
        raise UserError(msg)
    return path


def get_mrs_build_data_path() -> pathlib.Path:
    return get_workspace_path() / _MRS_BUILD_DATA_DIR_NAME


def get_settings_file_path() -> pathlib.Path:
    settings_file_path = get_mrs_build_data_path() / _SETTINGS_FILE_NAME
    return settings_file_path


def get_cache_path() -> pathlib.Path:
    cache_dir = get_mrs_build_data_path() / _CACHE_DIR_NAME
    if not cache_dir.exists():
        cache_dir.mkdir()
    return cache_dir
