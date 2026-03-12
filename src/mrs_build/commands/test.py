import argparse
import dataclasses
import logging

from ..common.cli_args import (
    AllPackagesTag,
    add_package_param,
    create_alias_action,
    get_default_process_args,
)
from ..common.utils import get_install_env, run_colcon
from ..settings.settings import get_settings
from .command import Command

_logger = logging.getLogger(__name__)

_LINTER_LABEL = "^linter$"


@dataclasses.dataclass(frozen=True, kw_only=True)
class _TestArgs:
    package: str | AllPackagesTag
    pattern: str | None
    label: str | None
    use_install_environment: bool


def _configure_parser(parser: argparse.ArgumentParser):
    add_package_param(parser, allow_all=True)
    parser.add_argument(
        "--filter",
        type=str,
        default=None,
        dest="pattern",
        help="run only tests matching the specified filter",
    )
    parser.add_argument(
        "--label",
        type=str,
        default=None,
        help="run only tests matching the specified label",
    )
    parser.add_argument(
        "--use-install-environment",
        action="store_true",
        default=False,
        help="run the tests in workspace install environment",
    )
    parser.add_argument(
        "--lint",
        action=create_alias_action({"label": _LINTER_LABEL}),
        help="run only linter tests",
    )


def _test_command(args: _TestArgs) -> int:
    test_env = {}
    if args.use_install_environment:
        test_env.update(get_install_env())
    test_env.update(get_settings().environment)

    clear_command = ["colcon", "test-result", "--delete-yes"]
    test_command = [
        "colcon",
        "test",
        "--packages-select",
        args.package,
        "--event-handlers",
        "console_direct+",
        "console_stderr-",
        "console_start_end-",
    ]
    if args.pattern is not None:
        test_command += [
            "--ctest-args",
            "-R",
            args.pattern,
        ]
    if args.label is not None:
        test_command += [
            "--ctest-args",
            "-L",
            args.label,
        ]
    results_command = ["colcon", "test-result", "--all", "--verbose"]

    _logger.info("Clearing previous results...")
    result = run_colcon(clear_command, env=test_env)
    if result.returncode != 0:
        _logger.error("Failed to remove previous results!")
        return result.returncode

    _logger.info("Running tests...")
    result = run_colcon(test_command, env=test_env)
    if result.returncode != 0:
        _logger.error("Failed to run tests!")
        return result.returncode

    _logger.info("Showing results...")
    result = run_colcon(results_command)
    if result.returncode == 0:
        _logger.info("All tests successful.")
    else:
        _logger.error("Some tests failed!")

    return result.returncode


TEST_COMMAND = Command(
    configure_parser=_configure_parser,
    process_parsed=get_default_process_args(_TestArgs),
    entrypoint=_test_command,
    help="run tests for selected packages",
)
