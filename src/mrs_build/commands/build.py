import argparse
import dataclasses
import logging

from ..common.cli_args import (
    AllPackagesTag,
    add_package_param,
    get_default_process_args,
)
from ..common.utils import run_colcon
from ..settings.settings import get_settings
from .command import Command

_logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True, kw_only=True)
class _BuildArgs:
    package: str | AllPackagesTag
    skip_dependencies: bool


def _configure_parser(parser: argparse.ArgumentParser):
    add_package_param(parser, allow_all=True)
    parser.add_argument(
        "--skip-dependencies",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="enable/disable building of dependencies in the workspace",
    )


def _build_command(args: _BuildArgs) -> int:
    _logger.info("Running build...")
    build_env = get_settings().environment
    command = [
        "colcon",
        "build",
    ]
    match args.package:
        case AllPackagesTag():
            if args.skip_dependencies:
                _logger.warning("'skip-dependencies' has no effect here.")
            pass
        case str(package_name):
            if args.skip_dependencies:
                command.append("--packages-select")
            else:
                command.append("--packages-up-to")
            command.append(package_name)
    _logger.debug(f"Colcon invocation:\n`{command}`")
    result = run_colcon(
        command,
        env=build_env,
    )
    if result.returncode == 0:
        _logger.info("Build successful.")
    else:
        _logger.error("Build failed!")
    return result.returncode


BUILD_COMMAND = Command(
    configure_parser=_configure_parser,
    process_parsed=get_default_process_args(_BuildArgs),
    entrypoint=_build_command,
    help="build selected packages",
)
