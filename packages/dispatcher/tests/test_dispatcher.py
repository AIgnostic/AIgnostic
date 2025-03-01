from typing import List
import uuid

from common.models.pipeline import MetricCalculationJob, PipelineJob
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from dispatcher.dispatcher import Dispatcher
from dispatcher.models import RunningJob


@pytest.mark.asyncio
async def test_should_load_job_to_redis_and_dispatch():
    """Should load a job onto redis"""
    # Mock the Redis client
    mock_redis_client = AsyncMock()

    # Mock the connection
    mock_connection = MagicMock()

    # Create a Dispatcher instance with the mocked Redis client and connection
    dispatcher = Dispatcher(mock_connection, mock_redis_client)

    dispatcher.dispatch_as_required = AsyncMock()

    # Create a sample job
    job = PipelineJob(
        job_id=str(uuid.uuid4()),
        max_concurrent_batches=5,
        batch_size=10,
        batches=10,
        metrics=MetricCalculationJob(
            data_url="http://example.com/data",
            model_url="http://example.com/model",
            data_api_key="data_api_key",
            model_api_key="model_api_key",
            metrics=["accuracy"],
            model_type="model_type",
        ),
    )

    # Call process_new_job with the sample job
    await dispatcher.process_new_job(job)

    # Check if the job was added to Redis
    mock_redis_client.set.assert_called_once()
    args, kwargs = mock_redis_client.set.call_args
    args: List[str]
    running_job = RunningJob(
        job_data=job,
        currently_running_batches=0,
        completed_batches=0,
        errored_batches=0,
        pending_batches=10,
    )
    assert str(job.job_id) in args[0]
    assert args[1] == running_job.model_dump_json()
    assert dispatcher.dispatch_as_required.called
