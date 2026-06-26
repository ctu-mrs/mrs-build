import datetime
import logging
import sys
from typing import Any, TextIO


class Color:
    RESET = "\u001b[0m"
    BLACK = "\u001b[30m"
    RED = "\u001b[31m"
    GREEN = "\u001b[32m"
    YELLOW = "\u001b[33m"
    BLUE = "\u001b[34m"
    MAGENTA = "\u001b[35m"
    CYAN = "\u001b[36m"
    WHITE = "\u001b[37m"

    @classmethod
    def format(cls, color: str, data: str):
        return color + data + cls.RESET


class ColorFormatter(logging.Formatter):
    """Formatter for more colorful logging."""

    LEVEL_NAME_WIDTH = 8

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def level_to_color(self, level: str):
        if level == "CRITICAL":
            return Color.MAGENTA
        elif level == "ERROR":
            return Color.RED
        elif level == "WARNING":
            return Color.YELLOW
        elif level == "INFO":
            return Color.GREEN
        elif level == "DEBUG":
            return Color.CYAN
        else:
            return Color.BLUE

    def format(self, record: logging.LogRecord) -> str:
        color = self.level_to_color(record.levelname)
        result = ""
        # data / time
        result += datetime.datetime.fromtimestamp(record.created).strftime(
            "[%Y-%m-%d %H:%M:%S]"
        )

        # level
        result += color
        result += Color.format(color, f" [{record.levelname}]")
        result += " " * (
            max(0, self.LEVEL_NAME_WIDTH - len(record.levelname)) + 1
        )
        # logger and source method names
        result += record.name
        result += " -> "
        result += record.funcName
        # message
        if record.msg is not None:
            result += "\n"
            LINE_DECORATION = Color.format(color, "| ")
            result += LINE_DECORATION
            result += ("\n" + LINE_DECORATION).join(str(record.msg).split("\n"))

        return result


def initialize_color_logger(
    logger: logging.Logger,
    level: int = logging.WARNING,
    stream: TextIO = sys.stderr,
) -> None:
    handler = logging.StreamHandler(stream=stream)
    formatter = ColorFormatter()
    handler.setLevel(0)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)


if __name__ == "__main__":
    initialize_color_logger(logging.getLogger(), level=logging.DEBUG)

    logging.debug("Test of debug.")
    logging.info("Test of info.")
    logging.warning("Test of warning.")
    logging.error("Test of error.")
    logging.critical("Test of critical.")
