"""Hello unit test module."""

from common.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello models"
