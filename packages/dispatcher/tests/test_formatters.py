import logging
from dispatcher.logging.formatters import (
    strip_ansi,
    CustomFormatterWithFunctionDebugData,
    ColoredFormatterDev,
    ColoredFormatterProd,
    LOG_LEVEL_COLORS,
)


def test_strip_ansi():
    ansi_string = "\x1B[31mThis is red text\x1B[0m"
    assert strip_ansi(ansi_string) == "This is red text"


def test_custom_formatter_with_function_debug_data():
    formatter = CustomFormatterWithFunctionDebugData("%(func_lineno)s - %(message)s")
    record = logging.LogRecord(
        name="test",
        level=logging.DEBUG,
        pathname=__file__,
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
        funcName="test_func",
    )
    record.funcName = "test_func"
    formatted_message = formatter.format(record)
    assert "test_func():L10 - Test message" in formatted_message


def test_colored_formatter_dev():
    formatter = ColoredFormatterDev()
    record = logging.LogRecord(
        name="test",
        level=logging.DEBUG,
        pathname=__file__,
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    formatted_message = formatter.format(record)
    assert LOG_LEVEL_COLORS["DEBUG"] in formatted_message


def test_colored_formatter_prod():
    formatter = ColoredFormatterProd()
    record = logging.LogRecord(
        name="test",
        level=logging.DEBUG,
        pathname=__file__,
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    formatted_message = formatter.format(record)
    assert LOG_LEVEL_COLORS["DEBUG"] in formatted_message
