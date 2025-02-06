"""Hello unit test module."""

from aggregator.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello aggregator"
