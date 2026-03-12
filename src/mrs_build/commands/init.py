import argparse
import dataclasses
import pathlib

from ..common.cli_args import get_default_process_args
from ..common.workspace import initialize_workspace
from .command import Command


@dataclasses.dataclass
class InitArgs:
    path: pathlib.Path


def _configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "path",
        nargs="?",
        type=pathlib.Path,
        default=pathlib.Path(),  # default to cwd
        help="workspace directory to initialize",
    )


def init(args: InitArgs) -> None:
    initialize_workspace(args.path)


INIT_COMMAND = Command(
    configure_parser=_configure_parser,
    process_parsed=get_default_process_args(InitArgs),
    entrypoint=init,
    help="initialize new workspace",
)
