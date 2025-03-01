import json
import uuid

from common.models.pipeline import Batch, MetricCalculationJob
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from common.models import MetricConfig, MetricValue


from worker.worker import Worker

worker = Worker()


@patch("worker.worker.connect_to_rabbitmq")
@patch("worker.worker.init_queues")
def test_connect_worker(mock_init_queues, mock_connect_to_rabbitmq):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_connect_to_rabbitmq.return_value = mock_connection
    mock_connection.channel.return_value = mock_channel

    worker = Worker()
    worker.connect()

    mock_connect_to_rabbitmq.assert_called_once()
    mock_connection.channel.assert_called_once()
    mock_init_queues.assert_called_once_with(mock_channel)


def test_fetch_job_success():

    mock_method_frame = MagicMock()
    mock_header_frame = MagicMock()
    mock_body = (
        Batch(
            job_id=str(uuid.uuid4()),
            batch_id=uuid.uuid4(),
            batch_size=10,
            metrics=MetricCalculationJob(
                data_url="http://example.com/data",
                model_url="http://example.com/model",
                data_api_key="data_key",
                model_api_key="model_key",
                metrics=["accuracy"],
                model_type="binary classification",
            ),
        )
        .json()
        .encode("utf-8")
    )

    with patch.object(worker, "_channel", new_callable=MagicMock) as mock_channel:
        mock_channel.basic_get.return_value = (
            mock_method_frame,
            mock_header_frame,
            mock_body,
        )

        result = worker.fetch_batch()
        assert isinstance(result, Batch)
        assert str(result.metrics.data_url) == "http://example.com/data"


def test_fetch_job_no_job():

    with patch.object(worker, "_channel", new_callable=MagicMock) as mock_channel:
        mock_channel.basic_get.return_value = (None, None, None)
        result = worker.fetch_batch()
        assert result is None


def test_queue_result():
    with patch.object(worker, "_channel", new_callable=MagicMock) as mock_channel:
        result = MetricConfig(
            metric_values={
                "accuracy": MetricValue(
                    computed_value=0.95, ideal_value=1, range=(0, 1)
                )
            },
            batch_size=1,
            total_sample_size=1,
        )
        worker.queue_result(result)
        mock_channel.basic_publish.assert_called_once()


def test_queue_error():
    with patch.object(worker, "_channel", new_callable=MagicMock) as mock_channel:
        error_message = "Some error occurred"
        worker.queue_error(error_message)
        mock_channel.basic_publish.assert_called_once()


@patch(
    "metrics.metrics.calculate_metrics",
    return_value=MetricConfig(
        metric_values={
            "accuracy": MetricValue(computed_value=0.95, ideal_value=1, range=(0, 1))
        },
        batch_size=1,
        total_sample_size=1,
    ),
)
@pytest.mark.asyncio
async def test_process_job_success(mock_calculate_metrics):
    job = Batch(
        job_id=str(uuid.uuid4()),
        batch_id=uuid.uuid4(),
        batch_size=1,
        metrics=MetricCalculationJob(
            data_url="http://example.com/data",
            model_url="http://example.com/model",
            data_api_key="data_key",
            model_api_key="model_key",
            metrics=["accuracy"],
            model_type="binary classification",
        ),
    )

    with patch.object(
        worker, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch_data, patch.object(
        worker, "query_model", new_callable=AsyncMock
    ) as mock_query_model, patch.object(
        worker, "queue_result", new_callable=MagicMock
    ) as mock_queue_result:

        mock_fetch_data.return_value = {
            "features": [[1, 2], [3, 4]],
            "labels": [[0], [1]],
            "group_ids": [1, 2],
        }
        mock_query_model.return_value = {
            "predictions": [[0], [1]],
            "confidence_scores": [[0.9], [0.8]],
        }

        await worker.process_job(job)

        mock_queue_result.assert_called_once()


@patch("worker.worker.requests.post")
@pytest.mark.asyncio
async def test_query_model_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"predictions": [[0], [1]]}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    data = {"features": [[1, 2]], "labels": [[0], [1]], "group_ids": [1]}
    result = await worker.query_model("http://example.com/model", data, "model_key")
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

    result = await worker.fetch_data("http://example.com/data", "data_key", 1)
    assert result["features"] == [[1, 2]]


def test_check_model_response():
    response = MagicMock()
    response.json.return_value = {"predictions": [[0, 1], [1, 0]]}
    labels = [[0, 1], [1, 0]]
    worker._check_model_response(response, labels)
