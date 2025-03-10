from report_generation.utils import search_legislation
from report_generation.utils import extract_legislation_text
from report_generation.utils import parse_legislation_text
from report_generation.utils import get_legislation_extracts
from report_generation.utils import add_llm_insights
from common.models import LegislationInfo
from unittest import mock
import pytest

EXTRACT = 'report_generation.utils.extract_legislation_text'
PARSE = 'report_generation.utils.parse_legislation_text'
LLM_INIT = 'llm_insights.insights.init_llm'
LLM_INSIGHTS = 'llm_insights.insights.metric_insights'


""" SEARCH LEGISLATION TESTS """


def test_search_legislation_with_valid_metric():
    metric = "fast gradient sign method"
    expected_output = []
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


# Helper function
def article_extension(article):
    return f"art-{article}-gdpr/"


def test_extract_legislation_text_with_valid_article():
    article_num = "31"
    url = "https://gdpr-info.eu/"
    article_31_text = extract_legislation_text(article_num, url, article_extension)
    assert "Art. 31" in article_31_text


def test_extract_legislation_text_with_non_existent_article():
    article_num = "999"
    url = "https://gdpr-info.eu/"
    result = extract_legislation_text(article_num, url, article_extension)
    assert "Failed to fetch Article 999." in result


def test_extract_legislation_text_with_invalid_response():
    with mock.patch('requests.get', return_value=mock.Mock(status_code=404)):
        article_num = "31"
        url = "https://invalid-url/"
        result = extract_legislation_text(article_num, url, article_extension)
    assert "Failed to fetch Article 31." in result


def test_extract_legislation_text_with_no_article_content():
    mock_response = mock.Mock(status_code=200,
                              text="<html><body></body></html>")
    with mock.patch('requests.get', return_value=mock_response):
        article = "31"
        url = "https://invalid-url/"
        result = extract_legislation_text(article, url, article_extension)
    assert "Could not parse content for Article 31." in result


""" PARSE LEGISLATION TESTS """


def test_parse_legislation_text_with_valid_content():
    article_num = "31"
    mock_name = "GDPR"
    mock_url = "https://gdpr-info.eu/"
    article_content = extract_legislation_text(article_num, mock_url, article_extension)
    expected_output = {
        "article_type": "GDPR",
        "article_number": "31",
        "article_title": "Cooperation with the supervisory authority",
        "link": "https://gdpr-info.eu/art-31-gdpr/",
        "description": "The controller and the processor and, where " +
        "applicable, their representatives, shall cooperate, on request, " +
        "with the supervisory authority in the performance of its tasks.",
        "suitable_recitals": ["https://gdpr-info.eu/recitals/no-82/"]
    }
    info = LegislationInfo(name=mock_name, url=mock_url, article_extract=article_extension)
    result = parse_legislation_text(article_num,
                                    article_content, info)
    print("Result", result)
    assert result == expected_output


def test_parse_legislation_text_with_multiple_recitals():
    article_num = "31"
    mock_name = "GDPR"
    mock_url = "https://gdpr-info.eu/"
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
        "article_type": "GDPR",
        "article_number": "31",
        "article_title": "Cooperation with the supervisory authority",
        "link": "https://gdpr-info.eu/art-31-gdpr/",
        "description": "The controller and the processor and, where " +
        "applicable, their representatives, shall cooperate, on request, " +
        "with the supervisory authority in the performance of its tasks.",
        "suitable_recitals": ["https://gdpr-info.eu/recitals/no-82/",
                              "https://gdpr-info.eu/recitals/no-81/"]
    }
    info = LegislationInfo(name=mock_name, url=mock_url, article_extract=article_extension)
    result = parse_legislation_text(article_num, article_content, info)
    assert result == expected_output


def test_parse_legislation_text_with_no_recitals():
    article = "31"
    mock_name = "GDPR"
    mock_url = "https://gdpr-info.eu/"
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
        "article_type": "GDPR",
        "article_number": "31",
        "article_title": "Cooperation with the supervisory authority",
        "link": "https://gdpr-info.eu/art-31-gdpr/",
        "description": "The controller and the processor and, " +
        "where applicable, their representatives, shall cooperate, " +
        "on request, with the supervisory authority " +
        "in the performance of its tasks.",
        "suitable_recitals": []
    }
    info = LegislationInfo(name=mock_name, url=mock_url, article_extract=article_extension)
    result = parse_legislation_text(article, article_content, info)
    assert result == expected_output


def test_parse_legislation_text_with_empty_content():
    article = "31"
    mock_name = "GDPR"
    mock_url = "https://gdpr-info.eu/"
    article_content = ""
    expected_output = {
        "article_type": "GDPR",
        "article_number": "31",
        "article_title": "",
        "link": "https://gdpr-info.eu/art-31-gdpr/",
        "description": "",
        "suitable_recitals": []
    }
    info = LegislationInfo(name=mock_name, url=mock_url, article_extract=article_extension)
    result = parse_legislation_text(article, article_content, info)
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
                "link": "https://gdpr-info.eu/art-1-gdpr/",
                "description": "Description for Article 1.",
                "suitable_recitals": ["https://gdpr-info.eu/recitals/no-R1/"]
            }
        ]
        mock_llm_init.return_value = mock.Mock()
        mock_llm_insights.return_value = ""

        yield mock_extract, mock_parse, mock_llm_init, mock_llm_insights


def test_generate_report_with_valid_metrics(mock_dependencies):
    legislation_information = {
        "gdpr": LegislationInfo(
            name="GDPR",
            url="https://gdpr-info.eu/",
            article_extract=article_extension
        ),
        "eu_ai": LegislationInfo(
            name="EU AI Act",
            url="https://ai-act-law.eu/",
            article_extract=article_extension
        )
    }
    metrics_data = {
        "ood_auroc": {
            "value": 0.6,
            "ideal_value": 1,
            "range": (0, 1),
            "error": None
        },
        "equal_opportunity_difference": {
            "value": 0.5,
            "ideal_value": 0,
            "range": (-1, 1),
            "error": None
        }
    }

    result = get_legislation_extracts(metrics_data, legislation_information)

    assert result[0]["property"] == "fairness"
    assert result[0]["computed_metrics"] == [{
        "metric": "equal opportunity difference",
        "value": 0.5,
        "ideal_value": 0,
        "range": (-1, 1),
        "error": None
    }]

    assert result[2]["property"] == "uncertainty"
    assert result[2]["computed_metrics"] == [{
        "metric": "ood auroc",
        "value": 0.6,
        "ideal_value": 1,
        "range": (0, 1),
        "error": None
    }]
    # assert len(result[2]["legislation_extracts"][0][0]) == len(property_to_regulations["fairness"])
    # assert len(result[3]["legislation_extracts"][0][0]) == len(property_to_regulations["uncertainty"])


def test_generate_report_with_empty_metrics(mock_dependencies):
    metrics_data = {}
    legislation_information = {
        "gdpr": LegislationInfo(
            name="GDPR",
            url="https://gdpr-info.eu/",
            article_extract=lambda article_number: f"art-{article_number}-gdpr"
        ),
    }
    result = get_legislation_extracts(metrics_data, legislation_information)

    assert result[0]["computed_metrics"] == []
    assert result[1]["computed_metrics"] == []
    assert result[2]["computed_metrics"] == []
    assert result[3]["computed_metrics"] == []
    assert result[4]["computed_metrics"] == []
    assert result[5]["computed_metrics"] == []

    # assert len(result[0]["legislation_extracts"][0]) == len(property_to_regulations["adversarial robustness"])
    # assert len(result[1]["legislation_extracts"][0]) == len(property_to_regulations["explainability"])
    # assert len(result[2]["legislation_extracts"][0]) == len(property_to_regulations["fairness"])
    # assert len(result[3]["legislation_extracts"][0]) == len(property_to_regulations["uncertainity"])
    # assert len(result[4]["legislation_extracts"][0]) == len(property_to_regulations["privacy"])
    # assert len(result[5]["legislation_extracts"][0]) == len(property_to_regulations["data minimality"])


def test_generate_report_with_non_existent_metric(mock_dependencies):
    metrics_data = {
        "non-existent metric": {}
    }
    legislation_information = {
        "gdpr": LegislationInfo(
            name="GDPR",
            url="https://gdpr-info.eu/",
            article_extract=article_extension
        ),
    }

    result = get_legislation_extracts(metrics_data, legislation_information)

    assert result[0]["computed_metrics"] == []
    assert result[1]["computed_metrics"] == []
    assert result[2]["computed_metrics"] == []
    assert result[3]["computed_metrics"] == []
    assert result[4]["computed_metrics"] == []
    assert result[5]["computed_metrics"] == []

    # assert len(result[0]["legislation_extracts"][0]) == len(property_to_regulations["adversarial robustness"])
    # assert len(result[1]["legislation_extracts"][0]) == len(property_to_regulations["explainability"])
    # assert len(result[2]["legislation_extracts"][0]) == len(property_to_regulations["fairness"])
    # assert len(result[3]["legislation_extracts"][0]) == len(property_to_regulations["uncertainity"])
    # assert len(result[4]["legislation_extracts"][0]) == len(property_to_regulations["privacy"])
    # assert len(result[5]["legislation_extracts"][0]) == len(property_to_regulations["data minimality"])


def test_add_llm_insights(mock_dependencies):
    metrics_data = [
        {
            "property": "adversarial robustness",
            "computed_metrics": [
                {
                    "metric": "fast gradient sign method",
                    "value": 0.6,
                    "ideal_value": 1,
                    "range": (0, 1)
                }
            ],
            "legislation_extracts": [
                {
                    "article_number": "1",
                    "article_title": "Title for Article 1",
                    "link": "https://gdpr-info.eu/art-1-gdpr/",
                    "description": "Description for Article 1.",
                    "suitable_recitals": ["https://gdpr-info.eu/recitals/no-R1/"]
                }
            ]
        }
    ]

    result = add_llm_insights(metrics_data, api_key="test_key")

    assert result[0]["llm_insights"] and result[0]["llm_insights"] != []
