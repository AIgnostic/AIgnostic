# Copyright Kishan Sambhi 2025
# From gitlab.doc.ic.ac.uk/edtech/search

import logging
import re
from typing import Callable

from colorama import Back, Fore, Style

# From https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
# 7-bit C1 ANSI sequences
ansi_escape = re.compile(
    r"""
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
""",
    re.VERBOSE,
)


def strip_ansi(str_with_ansi: str) -> str:
    """"""
    return ansi_escape.sub("", str_with_ansi)


LOG_LEVEL_COLORS = {
    "INFO": Fore.GREEN,  # Green
    "WARNING": Fore.YELLOW,  # Yellow
    "ERROR": Fore.RED,  # Red
    "DEBUG": Fore.CYAN,  # Blue
    "RESET": Fore.RESET,  # Reset color
}


# Standard log format we use
def get_log_format_dev(log_level_color: str | int) -> str:
    return f"[{Style.DIM}%(asctime)s{Style.RESET_ALL} {Fore.MAGENTA}%(name)-50s {Fore.CYAN}%(func_lineno)-40s {log_level_color}%(levelname)-8s{LOG_LEVEL_COLORS['RESET']} {Back.RESET}] %(message)s"


def get_log_format_prod(log_level_color: str | int) -> str:
    return f"[{Style.DIM}%(asctime)s{Style.RESET_ALL} {Fore.MAGENTA}%(name)-20s {log_level_color}%(levelname)-8s{LOG_LEVEL_COLORS['RESET']} {Back.RESET}] %(message)s"


LOG_FORMAT_COLOURED = get_log_format_dev("")
LOG_FORMAT_COLOURED_PROD = get_log_format_prod("")
LOG_FORMAT_UNCOLOURED = strip_ansi(LOG_FORMAT_COLOURED)
LOG_FORMAT_UNCOLOURED_PROD = strip_ansi(LOG_FORMAT_COLOURED_PROD)


# Custom log formatters
class CustomFormatterWithFunctionDebugData(logging.Formatter):
    """Adds funcName and lineno to log records for use by other formatters"""

    def format(self, record):
        # Combine funcName and lineno as a group
        record.func_lineno = f"{record.funcName}():L{record.lineno}"
        return super().format(record)


class ColouredLogLevelFormatter(CustomFormatterWithFunctionDebugData):
    """Adds colour the log level"""

    def custom_format(
        self, record: logging.LogRecord, format_str_getter: Callable[[str | int], str]
    ):
        """Need to instantiate CustomFormatterWithFunctionDebugData as we change the log string!"""
        log_level_color = LOG_LEVEL_COLORS.get(record.levelname, "")
        format_str = format_str_getter(log_level_color)
        formatter = CustomFormatterWithFunctionDebugData(
            format_str, datefmt="%Y-%m-%d %H:%M:%S"
        )
        return formatter.format(record)


class ColoredFormatterDev(ColouredLogLevelFormatter):
    """Use this stdout formatter for coloured logs in dev mode"""

    def format(self, record):
        return self.custom_format(record, get_log_format_dev)


class ColoredFormatterProd(ColouredLogLevelFormatter):
    """Use this stdout formatter for coloured logs in prod mode - essentially like dev mode but without loads of info"""

    def format(self, record):
        return self.custom_format(record, get_log_format_prod)
