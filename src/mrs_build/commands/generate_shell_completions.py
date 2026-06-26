import argparse
import dataclasses

from argcomplete.shell_integration import (
    shellcode,  # pyright: ignore[reportUnknownVariableType]
)

from ..common.cli_args import get_default_process_args
from .command import Command


@dataclasses.dataclass
class _GenerateShellCompletionsArgs:
    shell: str


def _configure_parser(parser: argparse.ArgumentParser):
    parser.add_argument("shell", nargs="?", default="bash")


def _generate_shell_completion(args: _GenerateShellCompletionsArgs) -> None:
    code = shellcode(["mrs-build"], shell=args.shell)
    print(code)


GENERATE_SHELL_COMPLETION_COMMAND = Command(
    configure_parser=_configure_parser,
    process_parsed=get_default_process_args(_GenerateShellCompletionsArgs),
    entrypoint=_generate_shell_completion,
    help="write shell completion script to stdout",
)
