from report_generation.utils import search_legislation
from report_generation.utils import extract_legislation_text
from report_generation.utils import parse_legislation_text
from report_generation.utils import generate_report
from report_generation.constants import property_to_regulations
from unittest import mock
import pytest

EXTRACT = 'report_generation.utils.extract_legislation_text'
PARSE = 'report_generation.utils.parse_legislation_text'
LLM_INIT = 'llm_insights.insights.init_llm'
LLM_INSIGHTS = 'llm_insights.insights.metric_insights'


""" SEARCH LEGISLATION TESTS """


def test_search_legislation_with_valid_metric():
    metric = "fast gradient sign method"
    expected_output = ["15"]
    result = search_legislation(metric)
    assert result == expected_output


def test_search_legislation_with_multiple_articles():
    metric = "equal opportunity difference"
    expected_output = ["10", "15"]
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


""" EXTRACT LEGISLATION TESTS """


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


""" PARSE LEGISLATION TESTS """


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


@pytest.fixture(scope="module")
def mock_dependencies():
    with mock.patch(EXTRACT) as mock_extract, \
         mock.patch(PARSE) as mock_parse, \
         mock.patch(LLM_INIT) as mock_llm_init, \
         mock.patch(LLM_INSIGHTS) as mock_llm_insights:
        mock_extract.return_value = [
            "Art. 1 GDPR\nTitle for Article 1\n" +
            "Description for Article 1.\n" +
            "Suitable Recitals\n(\nR1\n)",
        ]
        mock_parse.return_value = [
            {
                "article_number": "1",
                "article_title": "Title for Article 1",
                "description": "Description for Article 1.",
                "suitable_recitals": ["https://gdpr-info.eu/recitals/no-R1/"]
            }
        ]
        mock_llm_init.return_value = mock.Mock()
        mock_llm_insights.return_value = ""

        yield mock_extract, mock_parse, mock_llm_init, mock_llm_insights


def test_generate_report_with_valid_metrics(mock_dependencies):
    metrics_data = {
        "fast_gradient_sign_method": {
            "value": 0.6,
            "ideal_value": 1,
            "range": (0, 1)
        },
        "equal_opportunity_difference": {
            "value": 0.5,
            "ideal_value": 0,
            "range": (-1, 1)
        }
    }

    result = generate_report(metrics_data, api_key="test_key")

    assert result[0]["property"] == "adversarial robustness"
    assert result[0]["computed_metrics"] == [{
        "metric": "fast gradient sign method",
        "info": {
            "value": 0.6,
            "ideal_value": 1,
            "range": (0, 1)
        }
    }]

    assert result[2]["property"] == "fairness"
    assert result[2]["computed_metrics"] == [{
        "metric": "equal opportunity difference",
        "info": {
            "value": 0.5,
            "ideal_value": 0,
            "range": (-1, 1)
        }
    }]
    assert len(result[0]["legislation_extracts"]) == len(property_to_regulations["adversarial robustness"])
    assert len(result[1]["legislation_extracts"]) == len(property_to_regulations["explainability"])
    assert len(result[2]["legislation_extracts"]) == len(property_to_regulations["fairness"])
    assert len(result[3]["legislation_extracts"]) == len(property_to_regulations["uncertainity"])
    assert len(result[4]["legislation_extracts"]) == len(property_to_regulations["privacy"])
    assert len(result[5]["legislation_extracts"]) == len(property_to_regulations["data minimality"])


def test_generate_report_with_empty_metrics(mock_dependencies):
    metrics_data = {}

    result = generate_report(metrics_data, api_key="test_key")

    assert result[0]["computed_metrics"] == []
    assert result[1]["computed_metrics"] == []
    assert result[2]["computed_metrics"] == []
    assert result[3]["computed_metrics"] == []
    assert result[4]["computed_metrics"] == []
    assert result[5]["computed_metrics"] == []

    assert len(result[0]["legislation_extracts"]) == len(property_to_regulations["adversarial robustness"])
    assert len(result[1]["legislation_extracts"]) == len(property_to_regulations["explainability"])
    assert len(result[2]["legislation_extracts"]) == len(property_to_regulations["fairness"])
    assert len(result[3]["legislation_extracts"]) == len(property_to_regulations["uncertainity"])
    assert len(result[4]["legislation_extracts"]) == len(property_to_regulations["privacy"])
    assert len(result[5]["legislation_extracts"]) == len(property_to_regulations["data minimality"])


def test_generate_report_with_non_existent_metric(mock_dependencies):
    metrics_data = {
        "non-existent metric": {}
    }

    result = generate_report(metrics_data, api_key="test_key")

    assert result[0]["computed_metrics"] == []
    assert result[1]["computed_metrics"] == []
    assert result[2]["computed_metrics"] == []
    assert result[3]["computed_metrics"] == []
    assert result[4]["computed_metrics"] == []
    assert result[5]["computed_metrics"] == []

    assert len(result[0]["legislation_extracts"]) == len(property_to_regulations["adversarial robustness"])
    assert len(result[1]["legislation_extracts"]) == len(property_to_regulations["explainability"])
    assert len(result[2]["legislation_extracts"]) == len(property_to_regulations["fairness"])
    assert len(result[3]["legislation_extracts"]) == len(property_to_regulations["uncertainity"])
    assert len(result[4]["legislation_extracts"]) == len(property_to_regulations["privacy"])
    assert len(result[5]["legislation_extracts"]) == len(property_to_regulations["data minimality"])
