from unittest.mock import MagicMock, patch
from llm_insights.insights import metric_insights
from llm_insights.prompt import construct_prompt


def test_metric_insights():
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

    mock_llm = MagicMock()
    mock_response = "Mocked LLM Response"
    mock_llm.invoke.return_value = mock_response  # Synchronous return value

    with patch("llm_insights.insights.construct_prompt", wraps=construct_prompt) as mock_construct_prompt:
        result = metric_insights(property_name, metrics, article_extracts, mock_llm)

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
