import pytest
from unittest.mock import AsyncMock, patch
from llm_insights.insights import metric_insights
from llm_insights.prompt import construct_prompt


@pytest.mark.asyncio
async def test_metric_insights():
    property_name = "Fairness"
    metric_name = "Bias"
    metric_value = "0.2"
    article_extracts = [
        {
            "article_number": "1",
            "article_title": "Title 1",
            "description": "Description 1",
        }
    ]
    mock_llm = AsyncMock()
    mock_response = "Mocked LLM Response"
    mock_llm.ainvoke.return_value = mock_response

    with patch(
        "llm_insights.insights.construct_prompt", wraps=construct_prompt
    ) as mock_construct_prompt:
        result = await metric_insights(
            property_name, metric_name, metric_value, article_extracts, mock_llm
        )

        # Check that the LLM is called
        mock_llm.ainvoke.assert_called_once()

        # Check that the response from the LLM is returned
        assert result == mock_response

        # Check that the prompt provided to the model matches the one from construct_prompt
        mock_construct_prompt.assert_called_once_with(
            property_name=property_name,
            metric_name=metric_name,
            metric_value=metric_value,
            article_extracts=article_extracts,
        )
