"""Hello unit test module."""

from aignostic.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello aignostic"
