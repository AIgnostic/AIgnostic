import json
import uuid

from common.models.common import WorkerError
from common.models.pipeline import Batch, MetricCalculationJob
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from common.models import (
    WorkerResults,
    MetricValue,
    MetricConfig,
    DatasetResponse,
    ModelResponse,
)
from metrics.models import WorkerException
from worker.worker import Worker
from requests.exceptions import HTTPError

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
            batch_id=str(uuid.uuid4()),
            batch_size=10,
            metrics=MetricCalculationJob(
                data_url="http://example.com/data",
                model_url="http://example.com/model",
                data_api_key="data_key",
                model_api_key="model_key",
                metrics=["accuracy"],
                model_type="binary_classification",
            ),
            total_sample_size=500,
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
            user_id="1234",
        )
        worker.queue_result(result)
        mock_channel.basic_publish.assert_called_once()


@patch("worker.worker.requests.get")
@patch("worker.worker.requests.post")
@pytest.mark.asyncio
async def test_process_job_with_user_defined_metrics(mock_post, mock_get):
    job = Batch(
        job_id=str(uuid.uuid4()),
        batch_id=str(uuid.uuid4()),
        batch_size=1,
        metrics=MetricCalculationJob(
            data_url="http://example.com/data",
            model_url="http://example.com/model",
            data_api_key="data_key",
            model_api_key="model_key",
            metrics=["accuracy"],
            model_type="binary_classification",
        ),
        total_sample_size=500,
    )

    with patch.object(
        worker, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch_data, patch.object(
        worker, "query_model", new_callable=AsyncMock
    ) as mock_query_model, patch.object(
        worker, "queue_result", new_callable=MagicMock
    ) as mock_queue_result, patch.object(
        worker, "send_status_completed", new_callable=MagicMock
    ) as mock_send_status_completed:

        mock_fetch_data.return_value = DatasetResponse(
            features=[[1, 2]], labels=[[0]], group_ids=[1]
        )
        mock_query_model.return_value = ModelResponse(
            predictions=[[0]], confidence_scores=[[0.9]]
        )

        mock_get.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value={"functions": ["user_metric_1"]}),
        )

        mock_post.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value={"result": {
                "computed_value": 0.85,
                "ideal_value": 1,
                "range": [0, 1]
            }}),
        )

        await worker.process_job(job)

        mock_queue_result.assert_called_once()
        mock_send_status_completed.assert_called_once()
        assert mock_queue_result.call_args[0][0].user_defined_metrics == {
            "user_metric_1": {
                "computed_value": 0.85,
                "ideal_value": 1,
                "range": [0, 1]
            }
        }


@patch("worker.worker.requests.get")
@patch("worker.worker.requests.post")
@pytest.mark.asyncio
async def test_process_job_user_defined_metrics_server_error(mock_post, mock_get):
    job = Batch(
        job_id=str(uuid.uuid4()),
        batch_id=str(uuid.uuid4()),
        batch_size=1,
        metrics=MetricCalculationJob(
            data_url="http://example.com/data",
            model_url="http://example.com/model",
            data_api_key="data_key",
            model_api_key="model_key",
            metrics=["accuracy"],
            model_type="binary_classification",
        ),
        total_sample_size=500,
    )

    with patch.object(
        worker, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch_data, patch.object(
        worker, "query_model", new_callable=AsyncMock
    ) as mock_query_model, patch.object(
        worker, "queue_result", new_callable=MagicMock
    ) as mock_queue_result, patch.object(
        worker, "send_status_completed", new_callable=MagicMock
    ) as mock_send_status_completed:

        mock_fetch_data.return_value = DatasetResponse(
            features=[[1, 2]], labels=[[0]], group_ids=[1]
        )
        mock_query_model.return_value = ModelResponse(
            predictions=[[0]], confidence_scores=[[0.9]]
        )

        mock_get.return_value = MagicMock(
            status_code=500,
            text="Internal Server Error",
        )

        await worker.process_job(job)

        mock_queue_result.assert_called_once()
        mock_send_status_completed.assert_called_once()
        assert mock_queue_result.call_args[0][0].user_defined_metrics is None


@patch("worker.worker.requests.delete")
@patch("worker.worker.requests.get")
@patch("worker.worker.requests.post")
@pytest.mark.asyncio
async def test_process_job_clear_user_data_on_success(mock_post, mock_get, mock_delete):
    job = Batch(
        job_id=str(uuid.uuid4()),
        batch_id=str(uuid.uuid4()),
        batch_size=1,
        metrics=MetricCalculationJob(
            data_url="http://example.com/data",
            model_url="http://example.com/model",
            data_api_key="data_key",
            model_api_key="model_key",
            metrics=["accuracy"],
            model_type="binary_classification",
        ),
        total_sample_size=500,
    )

    with patch.object(
        worker, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch_data, patch.object(
        worker, "query_model", new_callable=AsyncMock
    ) as mock_query_model, patch.object(
        worker, "queue_result", new_callable=MagicMock
    ) as mock_queue_result, patch.object(
        worker, "send_status_completed", new_callable=MagicMock
    ) as mock_send_status_completed:

        mock_fetch_data.return_value = DatasetResponse(
            features=[[1, 2]], labels=[[0]], group_ids=[1]
        )
        mock_query_model.return_value = ModelResponse(
            predictions=[[0]], confidence_scores=[[0.9]]
        )

        mock_get.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value={"functions": ["user_metric_1"]}),
        )

        mock_post.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value={"result": {
                "computed_value": 0.85,
                "ideal_value": 1,
                "range": [0, 1]
            }}),
        )

        await worker.process_job(job)

        mock_queue_result.assert_called_once()
        mock_send_status_completed.assert_called_once()


@patch("worker.worker.requests.get")
@patch("worker.worker.requests.post")
@pytest.mark.asyncio
async def test_process_job_user_defined_metrics_execution_error(mock_post, mock_get):
    job = Batch(
        job_id=str(uuid.uuid4()),
        batch_id=str(uuid.uuid4()),
        batch_size=1,
        metrics=MetricCalculationJob(
            data_url="http://example.com/data",
            model_url="http://example.com/model",
            data_api_key="data_key",
            model_api_key="model_key",
            metrics=["accuracy"],
            model_type="binary_classification",
        ),
        total_sample_size=500,
    )

    with patch.object(
        worker, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch_data, patch.object(
        worker, "query_model", new_callable=AsyncMock
    ) as mock_query_model, patch.object(
        worker, "queue_result", new_callable=MagicMock
    ) as mock_queue_result, patch.object(
        worker, "send_status_completed", new_callable=MagicMock
    ) as mock_send_status_completed:

        mock_fetch_data.return_value = DatasetResponse(
            features=[[1, 2]], labels=[[0]], group_ids=[1]
        )
        mock_query_model.return_value = ModelResponse(
            predictions=[[0]], confidence_scores=[[0.9]]
        )

        mock_get.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value={"functions": ["user_metric_1"]}),
        )

        mock_post.return_value = MagicMock(
            status_code=500,
            text="Internal Server Error",
        )

        await worker.process_job(job)

        mock_queue_result.assert_called_once()
        mock_send_status_completed.assert_called_once()
        assert mock_queue_result.call_args[0][0].user_defined_metrics is None


def test_queue_error():
    with patch.object(worker, "_channel", new_callable=MagicMock) as mock_channel:
        error_message = "Some error occurred"
        worker.queue_error(WorkerError(error_message=error_message, error_code=500))
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
        batch_id=str(uuid.uuid4()),
        batch_size=1,
        metrics=MetricCalculationJob(
            data_url="http://example.com/data",
            model_url="http://example.com/model",
            data_api_key="data_key",
            model_api_key="model_key",
            metrics=["accuracy"],
            model_type="binary_classification",
        ),
        total_sample_size=500,
    )

    with patch.object(
        worker, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch_data, patch.object(
        worker, "query_model", new_callable=AsyncMock
    ) as mock_query_model, patch.object(
        worker, "queue_result", new_callable=MagicMock
    ) as mock_queue_result, patch.object(
        worker, "send_status_completed", new_callable=MagicMock
    ) as mock_send_status_completed:

        mock_fetch_data.return_value = DatasetResponse(
            features=[[1, 2]], labels=[[0]], group_ids=[1]
        )
        mock_query_model.return_value = ModelResponse(
            predictions=[[0], [1]], confidence_scores=[[0.9], [0.8]]
        )

        await worker.process_job(job)

        mock_queue_result.assert_called_once()
        mock_send_status_completed.assert_called_once()


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


def test_invalid_job_format_raises_worker_exception():
    with patch.object(worker, "_channel", new_callable=MagicMock) as mock_channel:
        job = Batch(
            job_id=str(uuid.uuid4()),
            batch_id=str(uuid.uuid4()),
            batch_size=1,
            metrics=MetricCalculationJob(
                data_url="http://example.com/data",
                model_url="http://example.com/model",
                data_api_key="data_key",
                model_api_key="model_key",
                metrics=["accuracy"],
                model_type="binary_classification",
            ),
            total_sample_size=500,
        )
        job_dict = job.model_dump()
        job_dict.pop("metrics")  # now an invalid Job

        mock_channel.basic_get.return_value = (
            MagicMock(),
            MagicMock(),
            json.dumps(job_dict).encode("utf-8"),
        )

        with pytest.raises(WorkerException):
            worker.fetch_batch()
            mock_channel.basic_get.assert_called_once()


@patch("worker.worker.requests.get")
@pytest.mark.asyncio
async def test_fetch_data_http_error_gives_worker_exception(mock_get):
    """Test that WorkerException is raised when an HTTP error occurs."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError("HTTP Error")
    mock_get.return_value = mock_response

    with pytest.raises(WorkerException):
        await worker.fetch_data("http://example.com/data", "data_key", 1)


@patch("worker.worker.requests.get")
@pytest.mark.asyncio
async def test_fetch_data_invalid_data_format_gives_worker_exception(mock_get):
    """Test that WorkerException is raised when the data format is incorrect."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "invalid": "data"
    }  # Not matching DatasetResponse schema
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    with pytest.raises(WorkerException) as excinfo:
        await worker.fetch_data("http://example.com/data", "data_key", 1)

    assert "Data error - data returned from data provider of incorrect format" in str(
        excinfo.value
    )


@patch("worker.worker.requests.post")
@pytest.mark.asyncio
async def test_query_model_http_error_gives_worker_exception(mock_post):
    """Test that WorkerException is raised when an HTTP error occurs."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError("HTTP Error")
    mock_post.return_value = mock_response

    mock_data = DatasetResponse(features=[[1, 2]], labels=[[0]], group_ids=[1])

    with pytest.raises(WorkerException):
        await worker.query_model("http://example.com/predict", mock_data, "model_key")


@patch("worker.worker.requests.post")
@pytest.mark.asyncio
async def test_query_model_invalid_data_format_gives_worker_exception(mock_post):
    """Test that WorkerException is raised when the data format is incorrect."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "invalid": "data"
    }  # Not matching ModelResponse schema
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    mock_data = DatasetResponse(features=[[1, 2]], labels=[[0]], group_ids=[1])
    with pytest.raises(WorkerException) as excinfo:
        await worker.query_model("http://example.com/predict", mock_data, "model_key")

    assert "Could not parse model response" in str(excinfo.value)


@pytest.mark.asyncio
async def test_worker_exception_during_process_job_send_error_to_frontend():
    job = Batch(
        job_id=str(uuid.uuid4()),
        batch_id=str(uuid.uuid4()),
        batch_size=1,
        metrics=MetricCalculationJob(
            data_url="http://example.com/data",
            model_url="http://example.com/model",
            data_api_key="data_key",
            model_api_key="model_key",
            metrics=["accuracy"],
            model_type="binary_classification",
        ),
        total_sample_size=500,
    )

    with patch.object(
        worker, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch_data, patch.object(
        worker, "query_model", new_callable=AsyncMock
    ) as mock_query_model, patch.object(
        worker, "queue_error", new_callable=MagicMock
    ) as mock_queue_error, patch.object(
        worker, "send_status_error", new_callable=MagicMock
    ) as mock_send_status_error:

        mock_fetch_data.return_value = DatasetResponse(
            features=[[1, 2]], labels=[[0]], group_ids=[1]
        )

        mock_query_model.side_effect = WorkerException("Some error occurred")

        await worker.process_job(job)

        mock_queue_error.assert_called_once()
        mock_send_status_error.assert_called_once()
