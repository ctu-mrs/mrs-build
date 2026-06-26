from typing import Any

from .build import BUILD_COMMAND
from .command import Command
from .generate_shell_completions import GENERATE_SHELL_COMPLETION_COMMAND
from .init import INIT_COMMAND
from .list import LIST_COMMAND
from .test import TEST_COMMAND

COMMANDS: dict[str, Command[Any]] = {
    "init": INIT_COMMAND,
    "list": LIST_COMMAND,
    "build": BUILD_COMMAND,
    "test": TEST_COMMAND,
    "generate-shell-completion": GENERATE_SHELL_COMPLETION_COMMAND,
}
