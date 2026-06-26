import logging
import os
import pathlib
import re
import subprocess
import xml.etree.ElementTree as ET
from typing import Any, Optional

from .cache import get_cache_data, update_cache
from .errors import UserError
from .workspace import get_workspace_path

_logger = logging.getLogger(__name__)


def _get_default_colcon_env() -> dict[str, str]:
    env = os.environ.copy()
    to_remove = [
        "_ARGCOMPLETE",
        "COMP_LINE",
        "_ARGCOMPLETE_SUPPRESS_SPACE",
        "_ARGCOMPLETE_SHELL",
        "COMP_TYPE",
        "COMP_POINT",
    ]
    for arg in to_remove:
        if arg in env:
            del env[arg]
    return env


def run_colcon(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
    env = _get_default_colcon_env()
    if "env" in kwargs:
        env.update(kwargs["env"])
        del kwargs["env"]
    return subprocess.run(
        *args, **kwargs, env=env, cwd=get_workspace_path()
    )  # pyright: ignore[reportReturnType]


def find_package_for_path(path: pathlib.Path | str):
    path = pathlib.Path(path)
    path = path.resolve()
    assert path.exists()
    if path.is_file():
        dir = path.parent
    elif path.is_dir():
        dir = path
    else:
        raise UserError("Unknown file type for obtaining package")
    while not (dir / "package.xml").exists():
        new_dir = dir.parent
        if new_dir == dir:
            # We reached filesystem root
            raise UserError("Provided path is not in a ROS package")
        dir = new_dir
    try:
        package_name = get_package_name(dir / "package.xml")
    except Exception as e:
        _logger.error("Failed to parse package.xml")
        _logger.debug(f"Parsing error: {e}")
        raise UserError("Package.xml corrupted")
    _logger.info(f"Found package name '{package_name}'")
    return package_name


def get_package_name(package_xml_path: pathlib.Path) -> Optional[str]:
    tree = ET.parse(package_xml_path)
    root = tree.getroot()
    name_element = root.find("name")
    if name_element is None:
        raise RuntimeError("Could not find name in package.xml")
    return name_element.text


def get_package_path(package: str) -> pathlib.Path:
    result = subprocess.run(["colcon", "info", package], capture_output=True)
    if result.returncode != 0:
        raise UserError(
            "Error while searching for package.\n"
            + "stderr:\n"
            + result.stderr.decode()
        )
    lines = result.stdout.decode().splitlines()
    assert len(lines) > 0
    line = lines[0]
    match_result = re.match(r"path: (.*)", line)
    assert match_result
    path = pathlib.Path(match_result.group(1))
    assert path.is_dir()
    return path


_PACKAGE_LIST_CACHE_KEY = "packages.txt"


def get_packages_list() -> list[str]:
    result = run_colcon(["colcon", "list", "--names-only"], capture_output=True)
    data = result.stdout.decode()
    packages = data.splitlines()
    update_cache(_PACKAGE_LIST_CACHE_KEY, data)
    return packages


def get_cached_packages_list(max_age_s: float | None = None) -> list[str]:
    data = get_cache_data(_PACKAGE_LIST_CACHE_KEY, max_age_s=max_age_s)
    if data is not None:
        return data.splitlines()
    else:
        loaded = get_packages_list()
        return loaded


def get_install_env() -> dict[str, str]:
    default_env = _get_default_colcon_env()
    res = subprocess.run(
        ". ./install/setup.sh && env",
        shell=True,
        capture_output=True,
        env=default_env,
        cwd=get_workspace_path(),
    )
    if res.returncode != 0:
        _logger.error("Failed to get install environment.")
        _logger.debug(
            f"Failed to get install environment:\n{res.stderr.decode()}"
        )
        raise RuntimeError("failed to get install env")
    output = res.stdout.decode()
    env: dict[str, str] = {}
    for line in output.splitlines():
        name, val = line.split("=", maxsplit=1)
        assert name not in env
        env[name] = val
    return env
