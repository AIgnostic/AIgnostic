"""Hello unit test module."""

from models.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello models"
