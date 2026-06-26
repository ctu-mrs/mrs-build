import argparse
import dataclasses
from typing import Any


@dataclasses.dataclass(frozen=True, kw_only=True)
class CommonArgs:
    subcommand: str
    verbose: bool


def configure_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="enable verbose output",
    )


def extract_common_args(args: argparse.Namespace) -> CommonArgs:
    common_args: dict[str, Any] = {}
    for field in dataclasses.fields(CommonArgs):
        name = field.name
        common_args[name] = getattr(args, name)
        delattr(args, name)
    return CommonArgs(**common_args)
