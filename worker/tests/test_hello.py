"""Hello unit test module."""

from worker.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello worker"
