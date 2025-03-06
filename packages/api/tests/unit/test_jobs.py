from unittest.mock import patch, MagicMock
import uuid
from api.router.api import dispatch_job
from common.models.pipeline import MetricCalculationJob
from common.rabbitmq.constants import JOB_QUEUE


def test_dispatch_job():
    # Mock the channel object returned by the connection
    mock_publisher = MagicMock()

    # Sample data for testing
    metrics = ["accuracy", "precision"]
    data_url = "https://example.com/data"
    model_url = "https://example.com/model"
    data_api_key = "data-key"
    model_api_key = "model-key"

    # Dispatch job

    dispatch_job(
        metrics=MetricCalculationJob(
            data_url=data_url,
            model_url=model_url,
            data_api_key=data_api_key,
            model_api_key=model_api_key,
            metrics=metrics,
            model_type="binary classification",
        ),
        batches=10,
        batch_size=10,
        max_concurrent_batches=1,
        publisher=mock_publisher,
        job_id=str(uuid.uuid4()),
    )

    # Assert that `publish` was called once
    mock_publisher.publish.assert_called_once()

    # Check publish called with a str
    args, _ = mock_publisher.publish.call_args
    assert isinstance(args[0], str)
