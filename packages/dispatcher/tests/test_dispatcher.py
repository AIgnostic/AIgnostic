import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from dispatcher.dispatcher import Dispatcher
from common.models.common import Job
from dispatcher.models import RunningJob


@pytest.mark.asyncio
async def test_should_load_job_to_redis():
    """Should load a job onto redis"""
    # Mock the Redis client
    mock_redis_client = AsyncMock()

    # Mock the connection
    mock_connection = MagicMock()

    # Create a Dispatcher instance with the mocked Redis client and connection
    dispatcher = Dispatcher(mock_connection, mock_redis_client)

    # Create a sample job
    job = Job(
        user_id="user123",
        max_concurrenct_batches=5,
        batch_size=10,
        total_sample_size=100,
        metrics=["accuracy"],
        model_type="linear",
        data_url="https://example.com/data",
        model_url="https://example.com/model",
        data_api_key="data_key",
        model_api_key="model_key",
    )

    # Call process_new_job with the sample job
    await dispatcher.process_new_job(job)

    # Check if the job was added to Redis
    mock_redis_client.set.assert_called_once()
    args, kwargs = mock_redis_client.set.call_args
    assert args[0] == job.user_id
    running_job = RunningJob(
        job_data=job,
        user_id=job.user_id,
        max_concurrent_batches=job.max_concurrenct_batches,
        currently_running_batches=0,
        completed_batches=0,
        errored_batches=0,
    )
    assert args[0] == job.user_id
    assert args[1] == running_job.model_dump_json()
