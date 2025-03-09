import pytest
from unittest.mock import AsyncMock, patch
from llm_insights.insights import metric_insights
from llm_insights.prompt import construct_articles, construct_prompt


@pytest.mark.asyncio
async def test_metric_insights():
    property_name = "Fairness"
    metrics = [
        {"metric": "Bias", "value": "0.2"},
        {"metric": "Representation", "value": "0.8"}
    ]
    article_extracts = [[
        {
            "article_type": "GDPR",
            "article_number": "1",
            "article_title": "Title 1",
            "description": "Description 1",
        }
    ]]
    mock_llm = AsyncMock()
    mock_response = "Mocked LLM Response"
    mock_llm.invoke.return_value = mock_response

    with patch(
        "llm_insights.insights.construct_prompt", wraps=construct_prompt
    ) as mock_construct_prompt:
        result = await metric_insights(
            property_name, metrics, article_extracts, mock_llm
        )

        # Check that the LLM is called
        mock_llm.invoke.assert_called_once()

        # Check that the response from the LLM is returned
        assert result == mock_response

        # Check that the prompt provided to the model matches the one from construct_prompt
        mock_construct_prompt.assert_called_once_with(
            property_name=property_name,
            metrics=metrics,
            article_extracts=article_extracts,
        )


def test_construct_articles():
    article_extracts = [[
        {
            "article_type": "GDPR",
            "article_number": "1",
            "article_title": "Title 1",
            "description": "Description 1",
        },
        {
            "article_type": "GDPR",
            "article_number": "2",
            "article_title": "Title 2",
            "description": "Description 2",
        },
    ]]
    result = construct_articles(article_extracts)
    assert "GDPR" in result
    assert "1" in result
    assert "Title 1" in result
    assert "Description 1" in result
    assert "2" in result
    assert "Title 2" in result
    assert "Description 2" in result

def test_construct_articles_empty():
    article_extracts = [[]]
    result = construct_articles(article_extracts)
    assert result == ""

def test_construct_articles_multiple_legislations():
    article_extracts = [
        [
            {
                "article_type": "GDPR",
                "article_number": "1",
                "article_title": "Title 1",
                "description": "Description 1",
            }
        ],
        [
            {
                "article_type": "CCPA",
                "article_number": "2",
                "article_title": "Title 2",
                "description": "Description 2",
            }
        ]
    ]
    result = construct_articles(article_extracts)
    assert "GDPR" in result
    assert "1" in result
    assert "Title 1" in result
    assert "Description 1" in result
    assert "CCPA" in result
    assert "2" in result
    assert "Title 2" in result
    assert "Description 2" in result

def test_construct_prompt():
    property_name = "Fairness"
    metrics = [
        {"metric": "Bias", "value": "0.2"},
        {"metric": "Representation", "value": "0.8"}
    ]
    article_extracts = [[
        {
            "article_type": "GDPR",
            "article_number": "1",
            "article_title": "Title 1",
            "description": "Description 1",
        }
    ]]
    result = construct_prompt(
        property_name, metrics, article_extracts
    )
    assert "Fairness" in result
    assert "Bias" in result
    assert "0.2" in result
    assert "Representation" in result
    assert "0.8" in result
    assert "1" in result
    assert "Title 1" in result
    assert "Description 1" in result
