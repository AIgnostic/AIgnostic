import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from aggregator.aggregator import (
    aggregator_app,
    fetch_result_from_queue,
    MetricsAggregatedResponse,
)

client = TestClient(aggregator_app)


@patch("aggregator.aggregator.channel")
def test_fetch_result_from_queue_success(mock_channel):
    mock_method_frame = MagicMock()
    mock_header_frame = MagicMock()
    mock_body = json.dumps({"metric_values": {"metric1": 100, "metric2": 200}}).encode(
        "utf-8"
    )
    mock_channel.basic_get.return_value = (mock_method_frame, mock_header_frame, mock_body)

    result = fetch_result_from_queue()
    expected_result = [
        {
            "metric": "metric1",
            "result": 100,
            "legislation_results": ["Placeholder"],
            "llm_model_summary": ["Placeholder"],
        },
        {
            "metric": "metric2",
            "result": 200,
            "legislation_results": ["Placeholder"],
            "llm_model_summary": ["Placeholder"],
        },
    ]
    assert result == expected_result


@patch("aggregator.aggregator.channel")
def test_fetch_result_from_queue_no_result(mock_channel):
    mock_channel.basic_get.return_value = (None, None, None)
    result = fetch_result_from_queue()
    assert result is None


@patch("aggregator.aggregator.channel")
def test_fetch_result_from_queue_error(mock_channel):
    mock_method_frame = MagicMock()
    mock_header_frame = MagicMock()
    mock_body = json.dumps({"error": "Some error occurred"}).encode("utf-8")
    mock_channel.basic_get.return_value = (mock_method_frame, mock_header_frame, mock_body)

    result = fetch_result_from_queue()
    expected_result = [{"error": "Some error occurred"}]
    assert result == expected_result


@patch("aggregator.aggregator.fetch_result_from_queue")
def test_get_results_success(mock_fetch_result_from_queue):
    mock_fetch_result_from_queue.return_value = [
        {
            "metric": "metric1",
            "result": 100,
            "legislation_results": ["Placeholder"],
            "llm_model_summary": ["Placeholder"],
        }
    ]
    response = client.get("/results")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Data successfully received",
        "results": [
            {
                "metric": "metric1",
                "result": 100,
                "legislation_results": ["Placeholder"],
                "llm_model_summary": ["Placeholder"],
            }
        ],
    }


@patch("aggregator.aggregator.fetch_result_from_queue")
def test_get_results_no_content(mock_fetch_result_from_queue):
    mock_fetch_result_from_queue.return_value = None
    response = client.get("/results")
    assert response.status_code == 204