import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from common.models.job import Job
from common.models import MetricValues, CalculateRequest
from pika.adapters.blocking_connection import BlockingChannel


from worker.worker import (
    start_worker,
    fetch_job,
    queue_result,
    queue_error,
    process_job,
    WorkerException,
    fetch_data,
    query_model,
    check_model_response,
)


@patch("worker.worker.connect_to_rabbitmq")
@patch("worker.worker.init_queues")
def test_start_worker(mock_init_queues, mock_connect_to_rabbitmq):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_connect_to_rabbitmq.return_value = mock_connection
    mock_connection.channel.return_value = mock_channel

    start_worker()

    mock_connect_to_rabbitmq.assert_called_once()
    mock_connection.channel.assert_called_once()
    mock_init_queues.assert_called_once_with(mock_channel)


@patch("worker.worker.channel.basic_get")
def test_fetch_job_success(mock_basic_get):
    mock_method_frame = MagicMock()
    mock_header_frame = MagicMock()
    mock_body = json.dumps(
        {
            "batch_size": 10,
            "metrics": ["accuracy"],
            "data_url": "http://example.com/data",
            "model_url": "http://example.com/model",
            "data_api_key": "data_key",
            "model_api_key": "model_key",
        }
    ).encode("utf-8")
    mock_basic_get.return_value = (mock_method_frame, mock_header_frame, mock_body)

    result = fetch_job()
    assert isinstance(result, Job)
    assert result.data_url == "http://example.com/data"


@patch("worker.worker.channel.basic_get")
def test_fetch_job_no_job(mock_basic_get):
    mock_basic_get.return_value = (None, None, None)
    result = fetch_job()
    assert result is None


@patch("worker.worker.channel.basic_publish")
def test_queue_result(mock_basic_publish):
    result = MetricValues(metric_values={"accuracy": 0.95})
    queue_result(result)
    mock_basic_publish.assert_called_once()


@patch("worker.worker.channel.basic_publish")
def test_queue_error(mock_basic_publish):
    error_message = "Some error occurred"
    queue_error(error_message)
    mock_basic_publish.assert_called_once()


@patch("worker.worker.fetch_data", new_callable=AsyncMock)
@patch("worker.worker.query_model", new_callable=AsyncMock)
@patch("metrics.metrics.calculate_metrics")
@patch("worker.worker.queue_result")
@pytest.mark.asyncio
async def test_process_job_success(
    mock_queue_result, mock_calculate_metrics, mock_query_model, mock_fetch_data
):
    job = Job(
        batch_size=1,
        metrics=["accuracy"],
        data_url="http://example.com/data",
        model_url="http://example.com/model",
        data_api_key="data_key",
        model_api_key="model_key",
    )
    mock_fetch_data.return_value = {
        "features": [[1, 2], [3, 4]],
        "labels": [[0], [1]],
        "group_ids": [1, 2],
    }
    mock_query_model.return_value = {"predictions": [[0], [1]]}
    mock_calculate_metrics.return_value = MetricValues(metric_values={"accuracy": 0.95})

    result = await process_job(job)
    assert result.metric_values["accuracy"] == 0.95
    mock_queue_result.assert_called_once()


@patch("worker.worker.requests.post")
@pytest.mark.asyncio
async def test_query_model_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"predictions": [[0], [1]]}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    data = {"features": [[1, 2]], "labels": [[0], [1]], "group_ids": [1]}
    result = await query_model("http://example.com/model", data, "model_key")
    assert result["predictions"] == [[0], [1]]


@patch("worker.worker.requests.get")
@pytest.mark.asyncio
async def test_fetch_data_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "features": [[1, 2]],
        "labels": [0],
        "group_ids": [1],
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = await fetch_data("http://example.com/data", "data_key")
    assert result["features"] == [[1, 2]]


def test_check_model_response():
    response = MagicMock()
    response.json.return_value = {"predictions": [[0, 1], [1, 0]]}
    labels = [[0, 1], [1, 0]]
    check_model_response(response, labels)
