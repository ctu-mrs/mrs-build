import argparse
import dataclasses
from collections.abc import Callable


@dataclasses.dataclass(frozen=True, kw_only=True)
class Command[T]:
    configure_parser: Callable[[argparse.ArgumentParser], None]
    process_parsed: Callable[[argparse.Namespace], T]
    entrypoint: Callable[[T], int | None]
    help: str | None = None
