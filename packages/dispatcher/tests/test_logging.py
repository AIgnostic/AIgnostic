import logging
import pytest
from dispatcher.logging.configure_logging import (
    configure_logging,
    configure_logging_dev,
    configure_logging_prod,
    configure_logging_common,
)


def test_configure_logging_common_debug():
    logger = logging.getLogger("test_logger")
    configure_logging_common(debug=True, logger_to_customise=logger)
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_configure_logging_common_info():
    logger = logging.getLogger("test_logger")
    configure_logging_common(debug=False, logger_to_customise=logger)
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_configure_logging_dev():
    logger = logging.getLogger("test_logger")
    configure_logging_dev(debug=True)
    assert logger.level == logging.DEBUG or logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_configure_logging_prod():
    logger = logging.getLogger("test_logger")
    configure_logging_prod(debug=True)
    assert logger.level == logging.DEBUG or logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_configure_logging_dev_environment():
    configure_logging(environment="dev", debug=True)
    root_logger = logging.getLogger("dispatcher")
    assert root_logger.level == logging.DEBUG or root_logger.level == logging.INFO
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0], logging.StreamHandler)


def test_configure_logging_prod_environment():
    configure_logging(environment="production", debug=True)
    root_logger = logging.getLogger("dispatcher")
    assert root_logger.level == logging.DEBUG or root_logger.level == logging.INFO
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0], logging.StreamHandler)


def test_configure_logging_trace():
    configure_logging(environment="dev", debug=True, trace=True)
    root_logger = logging.getLogger("dispatcher")
    assert root_logger.level == logging.DEBUG
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0], logging.StreamHandler)
