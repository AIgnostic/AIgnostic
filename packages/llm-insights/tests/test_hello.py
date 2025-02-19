"""Hello unit test module."""

from llm_insights.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello llm-insights"
