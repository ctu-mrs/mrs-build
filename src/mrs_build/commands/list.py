import argparse
import dataclasses

from ..common.cli_args import get_default_process_args
from ..common.utils import get_packages_list
from .command import Command


@dataclasses.dataclass
class ListArgs:
    pass


def _configure_parser(parser: argparse.ArgumentParser) -> None:
    pass


def _list_command(args: ListArgs) -> None:
    packages = get_packages_list()
    for package in packages:
        print(package)


LIST_COMMAND = Command(
    configure_parser=_configure_parser,
    process_parsed=get_default_process_args(ListArgs),
    entrypoint=_list_command,
    help="list packages in this workspace",
)
