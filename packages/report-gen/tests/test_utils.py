from report_gen.utils import search_legislation
from report_gen.utils import extract_legislation_text
from report_gen.utils import parse_legislation_text
from report_gen.utils import generate_report
from unittest import mock


def test_search_legislation_with_valid_metric():
    metric = "fast gradient sign method"
    expected_output = ["article 15"]
    result = search_legislation(metric)
    assert result == expected_output


def test_search_legislation_with_multiple_articles():
    metric = "equality of opportunity"
    expected_output = ["article 10", "article 15"]
    result = search_legislation(metric)
    assert result == expected_output


def test_search_legislation_with_non_existent_metric():
    metric = "non-existent metric"
    expected_output = []
    result = search_legislation(metric)
    assert result == expected_output


def test_search_legislation_with_empty_string():
    metric = ""
    expected_output = []
    result = search_legislation(metric)
    assert result == expected_output


def test_extract_legislation_text_with_valid_article():
    article_31_text = extract_legislation_text("31")
    assert "Art. 31" in article_31_text


def test_extract_legislation_text_with_non_existent_article():
    article = "999"
    result = extract_legislation_text(article)
    assert "Failed to fetch Article 999." in result


def test_extract_legislation_text_with_invalid_response():
    with mock.patch('requests.get', return_value=mock.Mock(status_code=404)):
        article = "31"
        result = extract_legislation_text(article)
    assert "Failed to fetch Article 31." in result


def test_extract_legislation_text_with_no_article_content():
    mock_response = mock.Mock(status_code=200,
                              text="<html><body></body></html>")
    with mock.patch('requests.get', return_value=mock_response):
        article = "31"
        result = extract_legislation_text(article)
    assert "Could not parse content for Article 31." in result


def test_parse_legislation_text_with_valid_content():
    article = "31"
    article_content = (
        "Art. 31 GDPR\n"
        "Cooperation with the supervisory authority\n"
        "The controller and the processor and, where applicable, "
        "their representatives, shall cooperate, on request, with "
        "the supervisory authority in the performance of its tasks.\n"
        "Suitable Recitals\n"
        "(\n"
        "82\n"
        ") Record of Processing Activities\n"
        "<-\n"
        "Art. 30 GDPR"
    )
    expected_output = {
        "article_number": "31",
        "article_title": "Cooperation with the supervisory authority",
        "description": "The controller and the processor and, where " +
        "applicable, their representatives, shall cooperate, on request, " +
        "with the supervisory authority in the performance of its tasks.",
        "suitable_recitals": ["https://gdpr-info.eu/recitals/no-82/"]
    }
    result = parse_legislation_text(article, article_content)
    assert result == expected_output


def test_parse_legislation_text_with_multiple_recitals():
    article = "31"
    article_content = """
    Art. 31 GDPR
    Cooperation with the supervisory authority
    The controller and the processor and, where applicable,
    their representatives, shall cooperate, on request,
    with the supervisory authority in the performance of its tasks.
    Suitable Recitals
    (
    82
    ) Record of Processing Activities
     (
    81
    ) Record of Processing Activities Second
    <-
    Art. 30 GDPR
    """
    expected_output = {
        "article_number": "31",
        "article_title": "Cooperation with the supervisory authority",
        "description": "The controller and the processor and, where " +
        "applicable, their representatives, shall cooperate, on request, " +
        "with the supervisory authority in the performance of its tasks.",
        "suitable_recitals": ["https://gdpr-info.eu/recitals/no-82/",
                              "https://gdpr-info.eu/recitals/no-81/"]
    }
    result = parse_legislation_text(article, article_content)
    assert result == expected_output


def test_parse_legislation_text_with_no_recitals():
    article = "31"
    article_content = """
    Art. 31 GDPR
    Cooperation with the supervisory authority
    The controller and the processor and, where applicable,
    their representatives, shall cooperate, on request,
    with the supervisory authority in the performance of its tasks.
    Suitable Recitals
    <-
    Art. 30 GDPR
    """
    expected_output = {
        "article_number": "31",
        "article_title": "Cooperation with the supervisory authority",
        "description": "The controller and the processor and, " +
        "where applicable, their representatives, shall cooperate, " +
        "on request, with the supervisory authority " +
        "in the performance of its tasks.",
        "suitable_recitals": []
    }
    result = parse_legislation_text(article, article_content)
    assert result == expected_output


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
    assert result == expected_output


def test_generate_report_with_valid_metrics():
    metrics_data = {
        "fast gradient sign method": {},
        "equality of opportunity": {}
    }
    expected_output = {
        "extracts": [
            {
                "article_number": "15",
                "article_title": "Title for Article 15",
                "description": "Description for Article 15.",
                "suitable_recitals": ["https://gdpr-info.eu/recitals/no-82/"]
            },
            {
                "article_number": "10",
                "article_title": "Title for Article 10",
                "description": "Description for Article 10.",
                "suitable_recitals": ["https://gdpr-info.eu/recitals/no-81/"]
            },
            {
                "article_number": "15",
                "article_title": "Title for Article 15",
                "description": "Description for Article 15.",
                "suitable_recitals": ["https://gdpr-info.eu/recitals/no-82/"]
            }
        ],
        "llm insights": []
    }

    with mock.patch('report_gen.utils.extract_legislation_text') as mock_extract, \
            mock.patch('report_gen.utils.parse_legislation_text') as mock_parse:
        mock_extract.side_effect = [
            "Art. 15 GDPR\nTitle for Article 15\nDescription for Article 15.\nSuitable Recitals\n(\n82\n)",
            "Art. 10 GDPR\nTitle for Article 10\nDescription for Article 10.\nSuitable Recitals\n(\n81\n)",
            "Art. 15 GDPR\nTitle for Article 15\nDescription for Article 15.\nSuitable Recitals\n(\n82\n)"
        ]
        mock_parse.side_effect = [
            {
                "article_number": "15",
                "article_title": "Title for Article 15",
                "description": "Description for Article 15.",
                "suitable_recitals": ["https://gdpr-info.eu/recitals/no-82/"]
            },
            {
                "article_number": "10",
                "article_title": "Title for Article 10",
                "description": "Description for Article 10.",
                "suitable_recitals": ["https://gdpr-info.eu/recitals/no-81/"]
            },
            {
                "article_number": "15",
                "article_title": "Title for Article 15",
                "description": "Description for Article 15.",
                "suitable_recitals": ["https://gdpr-info.eu/recitals/no-82/"]
            }
        ]

        result = generate_report(metrics_data)
        assert result == expected_output


def test_generate_report_with_empty_metrics():
    metrics_data = {}
    expected_output = {
        "extracts": [],
        "llm insights": []
    }
    result = generate_report(metrics_data)
    assert result == expected_output


def test_generate_report_with_non_existent_metric():
    metrics_data = {
        "non-existent metric": {}
    }
    expected_output = {
        "extracts": [],
        "llm insights": []
    }
    result = generate_report(metrics_data)
    assert result == expected_output
