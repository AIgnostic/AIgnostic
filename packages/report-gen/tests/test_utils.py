from report_gen.utils import search_legislation
from report_gen.utils import extract_legislation_text
from report_gen.utils import parse_legislation_text
from unittest import mock

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

def test_extract_legislation_text_with_valid_article():
    article_31_text = extract_legislation_text("31")
    assert "Art. 31" in article_31_text, "Test failed: Article 31 not found in output"

def test_extract_legislation_text_with_non_existent_article():
    article = "999"
    result = extract_legislation_text(article)
    assert "Failed to fetch Article 999." in result, "Test failed: Non-existent article should return an error."

def test_extract_legislation_text_with_invalid_response():
    with mock.patch('requests.get', return_value=mock.Mock(status_code=404)):
        article = "31"
        result = extract_legislation_text(article)
    assert "Failed to fetch Article 31." in result, "Test failed: Invalid response should return an error."

def test_extract_legislation_text_with_no_article_content():
    mock_response = mock.Mock(status_code=200, text="<html><body></body></html>")
    with mock.patch('requests.get', return_value=mock_response):
        article = "31"
        result = extract_legislation_text(article)
    assert "Could not parse content for Article 31." in result, "Test failed: No article content should return an error."
def test_parse_legislation_text_with_valid_content():
    article = "31"
    # article_content = """
    # Art. 31 GDPR Cooperation with the supervisory authority
    # 1. The controller and the processor and, where applicable, their representatives, shall cooperate, on request, with the supervisory authority in the performance of its tasks.
    # Suitable Recitals
    # 82
    # """
    article_content = extract_legislation_text(article)
    expected_output = {
        "article_number": "31",
        "article_title": "Cooperation with the supervisory authority",
        "description": "The controller and the processor and, where applicable, their representatives, shall cooperate, on request, with the supervisory authority in the performance of its tasks.",
        "suitable_recitals": ["https://gdpr-info.eu/recitals/no-82/"]
    }
    result = parse_legislation_text(article, article_content)
    print(result)
    assert result == expected_output, "Test failed: Valid content parsing error"


def test_parse_legislation_text_with_empty_content():
    article = "31"
    article_content = ""
    expected_output = {
        "article_number": "31",
        "article_title": "",
        "description": "",
        "suitable_recitals": []
    }
    result = parse_legislation_text(article, article_content)
    assert result == expected_output, "Test failed: Empty content parsing error"