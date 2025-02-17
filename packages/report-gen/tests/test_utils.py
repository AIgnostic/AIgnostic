from report_gen.utils import search_legislation


def test_search_legislation_with_valid_metric():
    metric = "fast gradient sign method"
    expected_output = {"article 15": "Placeholder"}
    result = search_legislation(metric)
    assert result == expected_output


def test_search_legislation_with_multiple_articles():
    metric = "equality of opportunity"
    expected_output = {"article 10": "Placeholder", "article 15": "Placeholder"}
    result = search_legislation(metric)
    assert result == expected_output


def test_search_legislation_with_non_existent_metric():
    metric = "non-existent metric"
    expected_output = {}
    result = search_legislation(metric)
    assert result == expected_output


def test_search_legislation_with_empty_string():
    metric = ""
    expected_output = {}
    result = search_legislation(metric)
    assert result == expected_output