import argparse
from collections.abc import Callable
from typing import Any, Iterable, Sequence

from .utils import find_package_for_path, get_cached_packages_list


class AllPackagesTag:
    pass


def package_completer(**kwargs: Any) -> list[str]:
    return get_cached_packages_list(max_age_s=5 * 60)


_JUNK_DEST_NAME = "_junk"


def postprocess_parsed(args: argparse.Namespace) -> argparse.Namespace:
    if hasattr(args, _JUNK_DEST_NAME):
        delattr(args, _JUNK_DEST_NAME)
    return args


def add_package_param(
    parser: argparse.ArgumentParser,
    *,
    dest: str = "package",
    allow_all: bool = False,
) -> None:
    package_selection_group = parser.add_mutually_exclusive_group(required=True)
    package_arg = package_selection_group.add_argument(
        "--package",
        type=str,
        default=None,
        dest=dest,
        help="select package by name",
        metavar="PACKAGE",
    )
    # `.completer` added is by argcomplete and not recognized by type checker
    package_arg.completer = package_completer  # pyright: ignore[reportAttributeAccessIssue] # fmt: skip
    package_selection_group.add_argument(
        "--path",
        type=find_package_for_path,
        default=None,
        dest=dest,
        metavar="PATH",
        help="select package containing the specified path",
    )
    if allow_all:
        package_selection_group.add_argument(
            "--all",
            action="store_const",
            const=AllPackagesTag(),
            dest=dest,
            help="select all packages in the workspace",
        )


def create_alias_action(values_to_set: dict[str, Any]):
    class _AliasAction[T](argparse.Action):
        def __init__(
            self,
            option_strings: Sequence[str],
            dest: str,
            nargs: int | str | None = None,
            const: T | None = None,
            default: T | str | None = None,
            type: Callable[[str], T] | argparse.FileType | None = None,
            choices: Iterable[T] | None = None,
            required: bool = False,
            help: str | None = None,
            metavar: str | tuple[str, ...] | None = None,
        ) -> None:
            assert nargs is None
            super().__init__(
                option_strings,
                _JUNK_DEST_NAME,
                0,
                const,
                default,
                type,
                choices,
                required,
                help,
                metavar,
            )

        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: str | Sequence[Any] | None,
            option_string: str | None = None,
        ) -> None:
            for key, val in values_to_set.items():
                setattr(namespace, key, val)

    return _AliasAction


def get_default_process_args[T](
    clazz: type[T],
) -> Callable[[argparse.Namespace], T]:
    def _process(args: argparse.Namespace) -> T:
        return clazz(**vars(args))

    return _process
