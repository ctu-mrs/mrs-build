import argparse
import logging

import argcomplete

from .commands import COMMANDS
from .common.cli_args import postprocess_parsed
from .common.logger import initialize_color_logger
from .common.utils import UserError
from .common_args import CommonArgs, configure_common_args, extract_common_args

_logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    configure_common_args(parser)
    subcommand_parsers = parser.add_subparsers(
        title="available commands",
        dest="subcommand",
        required=True,
        help="command to run",
        metavar="<command>",
    )
    for name, command in COMMANDS.items():
        subparser = subcommand_parsers.add_parser(name, help=command.help)
        command.configure_parser(subparser)
    return parser


def update_logging_level(args: CommonArgs) -> None:
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.getLogger().setLevel(level)


def run(common_args: CommonArgs, sub_args: argparse.Namespace) -> int | None:
    _logger.debug(common_args)
    _logger.debug(sub_args)
    subcommand_name = common_args.subcommand
    subcommand = COMMANDS.get(subcommand_name)
    if subcommand is None:
        raise UserError(f"Unknown command: '{subcommand_name}'")
    processed_args = subcommand.process_parsed(sub_args)
    return subcommand.entrypoint(processed_args)


def main() -> int | None:
    try:
        initialize_color_logger(logging.getLogger(), logging.WARNING)
        parser = build_parser()
        argcomplete.autocomplete(
            parser,
            "long",
        )
        args = parser.parse_args()
        args = postprocess_parsed(args)
        common_args = extract_common_args(args=args)
        update_logging_level(common_args)
        ret = run(common_args, args)
        return ret
    except UserError as e:
        _logger.error(f"UserError: {e}")
        return 1
    except KeyboardInterrupt:
        _logger.warning("Task interrupted.")
        return 1
