import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from common.models.common import Job
from common.models import WorkerResults, MetricValue, MetricConfig, DatasetResponse, ModelResponse


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
    mock_body = json.dumps(
        {
            "batch_size": 10,
            "total_sample_size": 100,
            "metrics": ["accuracy"],
            "model_type": "binary classification",
            "data_url": "http://example.com/data",
            "model_url": "http://example.com/model",
            "data_api_key": "data_key",
            "model_api_key": "model_key",
            "user_id": '1234'
        }
    ).encode("utf-8")

    with patch.object(worker, "_channel", new_callable=MagicMock) as mock_channel:
        mock_channel.basic_get.return_value = (mock_method_frame, mock_header_frame, mock_body)

        result = worker.fetch_job()
        assert isinstance(result, Job)
        assert result.data_url == "http://example.com/data"


def test_fetch_job_no_job():

    with patch.object(worker, "_channel", new_callable=MagicMock) as mock_channel:
        mock_channel.basic_get.return_value = (None, None, None)
        result = worker.fetch_job()
        assert result is None


def test_queue_result():
    with patch.object(worker, "_channel", new_callable=MagicMock) as mock_channel:
        result = WorkerResults(
            metric_values={
                "accuracy": MetricValue(
                    computed_value=0.95,
                    ideal_value=1,
                    range=(0, 1),
                )
            },
            batch_size=1,
            total_sample_size=1,
            user_id="1234"
        )
        worker.queue_result(result)
        mock_channel.basic_publish.assert_called_once()


def test_queue_error():
    with patch.object(worker, "_channel", new_callable=MagicMock) as mock_channel:
        error_message = "Some error occurred"
        worker.queue_error(error_message)
        mock_channel.basic_publish.assert_called_once()


@patch("metrics.metrics.calculate_metrics", return_value=MetricConfig(
    metric_values={
        "accuracy": MetricValue(
            computed_value=0.95,
            ideal_value=1,
            range=(0, 1)
        )
    },
    batch_size=1,
    total_sample_size=1
))
@pytest.mark.asyncio
async def test_process_job_success(mock_calculate_metrics):
    job = Job(
        batch_size=1,
        total_sample_size=1,
        metrics=["accuracy"],
        model_type="regression",  # use a model type that bypasses label conversion
        data_url="http://example.com/data",
        model_url="http://example.com/model",
        data_api_key="data_key",
        model_api_key="model_key",
        user_id="1234"
    )

    with patch.object(worker, "fetch_data", new_callable=AsyncMock) as mock_fetch_data, \
         patch.object(worker, "query_model", new_callable=AsyncMock) as mock_query_model, \
         patch.object(worker, "queue_result", new_callable=MagicMock) as mock_queue_result:

        mock_fetch_data.return_value = DatasetResponse(
            features=[[1, 2]],
            labels=[[0]],
            group_ids=[1]
        )
        mock_query_model.return_value = ModelResponse(
            predictions=[[0], [1]],
            confidence_scores=[[0.9], [0.8]]
        )

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
    data = DatasetResponse(**data)
    result = await worker.query_model("http://example.com/model", data, "model_key")
    assert result.predictions == [[0], [1]]


@patch("worker.worker.requests.get")
@pytest.mark.asyncio
async def test_fetch_data_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "features": [[1, 2]],
        "labels": [[0]],
        "group_ids": [1],
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = await worker.fetch_data("http://example.com/data", "data_key", 1)
    assert result.features == [[1, 2]]


def test_check_model_response():
    predictions = [[0, 1], [1, 0]]
    labels = [[0, 1], [1, 0]]
    worker._check_model_response(predictions, labels)
