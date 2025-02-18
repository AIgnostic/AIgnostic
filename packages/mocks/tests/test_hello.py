"""Hello unit test module."""

from packages.mocks.mocks.utils import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello mocks"
