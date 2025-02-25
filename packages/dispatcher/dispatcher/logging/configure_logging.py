# Copyright Kishan Sambhi 2025
# From gitlab.doc.ic.ac.uk/edtech/search
"""Configures server logging"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from os import path
from socket import gethostname

from dispatcher.logging.formatters import (
    LOG_FORMAT_UNCOLOURED,
    ColoredFormatterDev,
    ColoredFormatterProd,
    CustomFormatterWithFunctionDebugData,
)

logger = logging.getLogger(__name__)


def configure_logging_common(
    debug: bool = False,
    formatter_stdout: logging.Formatter = ColoredFormatterDev(),
    formatter_file: logging.Formatter = CustomFormatterWithFunctionDebugData(
        LOG_FORMAT_UNCOLOURED
    ),
    logger_to_customise: logging.Logger = logging.getLogger(__name__.split(".")[0]),
):
    """Common parameters for logging configuration - namely, the formatters"""
    # This sets the root logger to write to stdout (your console).
    # Your script/app needs to call this somewhere at least once.
    # (unless we use our own logger)
    # logging.basicConfig()

    # STDOUT/ERR colour logge
    handler = logging.StreamHandler()
    handler.setFormatter(formatter_stdout)

    # By default the root logger is set to WARNING and all loggers you define
    # inherit that value. Here we set the root logger to NOTSET. This logging
    # level is automatically inherited by all existing and new sub-loggers
    # that do not set a less verbose level.
    if debug:
        logger_to_customise.setLevel(logging.DEBUG)
    else:
        logger_to_customise.setLevel(logging.INFO)

    # Add dev handlers
    logger_to_customise.handlers = []
    logger_to_customise.addHandler(handler)


def configure_logging_dev(debug: bool = False):
    configure_logging_common(
        debug=debug,
        formatter_stdout=ColoredFormatterDev(),
        formatter_file=CustomFormatterWithFunctionDebugData(LOG_FORMAT_UNCOLOURED),
    )


def configure_logging_prod(debug: bool = False):
    """In prod, we have a custom formatter"""
    configure_logging_common(
        debug=debug,
        formatter_stdout=ColoredFormatterProd(),
        formatter_file=CustomFormatterWithFunctionDebugData(LOG_FORMAT_UNCOLOURED),
    )


def configure_logging(environment="dev", debug: bool = False, trace: bool = False):
    """Configure logging for the server. Environment can be 'dev' or 'production'."""
    # If trace mode, set the global logger to debug mode
    if trace:
        logging.getLogger().setLevel(logging.DEBUG)
        print("TRACE LOGGING SET.")

    if environment == "production":
        print("Using production logging config.")
        configure_logging_prod(debug=debug)
    else:
        print("Using dev logging config.")
        configure_logging_dev(debug=debug)
    logger.debug("Logging configured.")
