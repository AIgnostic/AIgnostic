from typing import List
import uuid

from common.models.pipeline import Batch, MetricCalculationJob, PipelineJob
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


@pytest.mark.asyncio
async def test_dispatch_batch_dispatches():
    """Should dispatch a batch"""
    # Mock the Redis client
    mock_redis_client = AsyncMock()

    # Mock the connection
    mock_connection = MagicMock()

    # Create a Dispatcher instance with the mocked Redis client and connection

    channel_mock = MagicMock()
    mock_connection.channel.return_value = channel_mock
    channel_mock.basic_publish = MagicMock()

    dispatcher = Dispatcher(mock_connection, mock_redis_client)

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

    # Create a sample batch
    batch = Batch(
        job_id=str(job.job_id),
        batch_id=str(uuid.uuid4()),
        batch_size=10,
        metrics=job.metrics,
    )

    # Call dispatch_batch with the job_id and the batch
    await dispatcher.dispatch_batch(job.job_id, batch)

    assert channel_mock.basic_publish.called
    args, kwargs = channel_mock.basic_publish.call_args
    assert kwargs["body"] == batch.model_dump_json()


@pytest.mark.parametrize(
    "pending_jobs, max_jobs, running_jobs",
    [
        (0, 5, 0),  # 0 pending, none dispatched
        (5, 5, 0),  # 5 pending, none running, so all dispatches
        (10, 5, 0),  # 10 pending, 5 max, so 5 dispatched
        (10, 5, 5),  # 10 pending, 5 running, 5 max allowed, so none dispatched
        (10, 5, 3),  # 10 pending, 3 running, 5 max allowed, so 2 dispatched
        (
            1000,
            1,
            2,
        ),  # 1000 pending, 1 running, 1 max allowed, but 2 running, should give none dispatched (error check)
    ],
)
@pytest.mark.asyncio
async def test_should_dispatch_new_batches_as_needed(
    pending_jobs, max_jobs, running_jobs
):
    job_spaces = max(0, max_jobs - running_jobs)
    expected_dispatched_batches = min(pending_jobs, job_spaces)
    job_id = str(uuid.uuid4())
    """Should dispatch new batches as required - until pending == max"""
    # Mock the Redis client
    mock_redis_client = AsyncMock()

    # Mock the connection
    mock_connection = MagicMock()

    # Create a Dispatcher instance with the mocked Redis client and connection
    dispatcher = Dispatcher(mock_connection, mock_redis_client)

    job = PipelineJob(
        job_id=job_id,
        max_concurrent_batches=max_jobs,
        batch_size=10,
        batches=10,  # should be ignored by dispatcher as we use pending jobs
        metrics=MetricCalculationJob(
            data_url="http://example.com/data",
            model_url="http://example.com/model",
            data_api_key="data_api_key",
            model_api_key="model_api_key",
            metrics=["accuracy"],
            model_type="model_type",
        ),
    )

    # Create a sample running job
    running_job = RunningJob(
        job_data=job,
        currently_running_batches=running_jobs,
        completed_batches=0,
        errored_batches=0,
        pending_batches=pending_jobs,
    )

    # Mock the get_job method
    dispatcher.get_job = AsyncMock()
    dispatcher.get_job.return_value = running_job

    # Mock the dispatch_batch method
    dispatcher.dispatch_batch = AsyncMock()

    # Mock the update_job method
    dispatcher.update_job = AsyncMock()

    # Call dispatch_as_required with the job_id
    await dispatcher.dispatch_as_required(job.job_id)

    # Check if the get_job method was called
    dispatcher.get_job.assert_called_once_with(job.job_id)

    # Check if the dispatch_batch method was called expected times & an update job for the pending batches
    assert dispatcher.dispatch_batch.call_count == expected_dispatched_batches
    assert dispatcher.update_job.call_count == expected_dispatched_batches

    # Check if the pending batches were updated
    if expected_dispatched_batches == 0:
        assert not dispatcher.update_job.called
        return

    args, kwargs = dispatcher.update_job.call_args
    assert args[0] == job.job_id
    updated_running_job = args[1]
    assert (
        updated_running_job.pending_batches
        == pending_jobs - expected_dispatched_batches
    )
    assert (
        updated_running_job.currently_running_batches
        == running_jobs + expected_dispatched_batches
    )

    # Should not delete the job if there are still pending batches
    assert not mock_redis_client.delete.called
