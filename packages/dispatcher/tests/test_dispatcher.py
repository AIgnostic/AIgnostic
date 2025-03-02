from typing import List
from unittest import mock
import uuid

from common.models.pipeline import Batch, MetricCalculationJob, PipelineJob
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from dispatcher.dispatcher import Dispatcher, DispatcherException
from dispatcher.models import RunningJob


@pytest.fixture
def mock_redis_client():
    """Fixture for creating a mock Redis client."""
    return AsyncMock()


@pytest.fixture
def mock_connection():
    """Fixture for creating a mock RabbitMQ connection."""
    connection_mock = MagicMock()
    connection_mock.channel = MagicMock()
    return connection_mock


@pytest.fixture
def dispatcher(mock_connection, mock_redis_client):
    """Fixture for creating a Dispatcher instance using the mock connection and Redis client."""
    return Dispatcher(mock_connection, mock_redis_client)


@pytest.fixture
def sample_job():
    """Fixture for creating a sample PipelineJob."""
    return PipelineJob(
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


def test_dispatcher_exception_has_detail_and_status_code():
    """Should have a detail and status code"""
    detail = "This is a test"
    status_code = 400
    exception = DispatcherException(detail, status_code)
    assert exception.detail == detail
    assert exception.status_code == status_code


def test_should_throw_dispatcher_exception_if_malformed_job(
    dispatcher, mock_connection
):
    """Should throw an exception if the job is malformed"""
    # Mock the channel's basic_get result
    mock_connection.channel.return_value.basic_get.return_value = (
        True,
        None,
        "malfomed job",
    )

    with pytest.raises(DispatcherException):
        dispatcher.fetch_job()


def test_should_unpack_job_correctly(dispatcher, mock_connection, sample_job):
    """Should correctly unpack a job from the job queue"""
    # Mock the channel's basic_get result
    mock_connection.channel.return_value.basic_get.return_value = (
        True,
        None,
        sample_job.model_dump_json(),
    )

    fetched_job = dispatcher.fetch_job()
    assert fetched_job == sample_job


def test_should_give_no_job_if_no_method_frame(dispatcher, mock_connection):
    """Should give no job if none found on the queue"""
    # Mock the channel's basic_get returning no job
    mock_connection.channel.return_value.basic_get.return_value = (None, None, None)

    fetched_job = dispatcher.fetch_job()
    assert fetched_job is None


@pytest.mark.asyncio
async def test_should_load_job_to_redis_and_dispatch(
    dispatcher, mock_redis_client, sample_job
):
    """Should load a job onto redis and start dispatching"""
    dispatcher.dispatch_as_required = AsyncMock()

    # Call process_new_job with the sample job
    await dispatcher.process_new_job(sample_job)

    # Check if the job was added to Redis
    mock_redis_client.set.assert_called_once()
    args, kwargs = mock_redis_client.set.call_args
    args: List[str]

    running_job = RunningJob(
        job_data=sample_job,
        currently_running_batches=0,
        completed_batches=0,
        errored_batches=0,
        pending_batches=10,
    )
    assert str(sample_job.job_id) in args[0]
    assert args[1] == running_job.model_dump_json()
    assert dispatcher.dispatch_as_required.called


@pytest.mark.asyncio
async def test_dispatch_batch_dispatches(mock_connection, sample_job):
    """Should dispatch a single batch"""
    channel_mock = MagicMock()
    mock_connection.channel.return_value = channel_mock
    channel_mock.basic_publish = MagicMock()

    dispatcher = Dispatcher(mock_connection, mock_redis_client)

    # Create a sample batch
    batch = Batch(
        job_id=str(sample_job.job_id),
        batch_id=str(uuid.uuid4()),
        batch_size=10,
        metrics=sample_job.metrics,
    )

    # Call dispatch_batch with the job_id and the batch
    await dispatcher.dispatch_batch(sample_job.job_id, batch)

    # Verify that a batch was published
    assert channel_mock.basic_publish.called
    args, kwargs = channel_mock.basic_publish.call_args
    assert kwargs["body"] == batch.model_dump_json()


@pytest.mark.parametrize(
    "pending_jobs, max_jobs, running_jobs",
    [
        # (pending_jobs, max_jobs, running_jobs)
        (0, 5, 0),  # 0 pending, none dispatched
        (5, 5, 0),  # 5 pending, none running, so all dispatches
        (10, 5, 0),  # 10 pending, 5 max, so 5 dispatched
        (10, 5, 5),  # 10 pending, 5 running, 5 max allowed, so none dispatched
        (10, 5, 3),  # 10 pending, 3 running, 5 max allowed, so 2 dispatched
        (1000, 1, 2),  # Many pending, already beyond max concurrency = 1
    ],
)
@pytest.mark.asyncio
async def test_should_dispatch_new_batches_as_needed(
    dispatcher, pending_jobs, max_jobs, running_jobs, mock_redis_client, sample_job
):
    """Should dispatch new batches as required - until pending == max"""
    job_spaces = max(0, max_jobs - running_jobs)
    expected_dispatched_batches = min(pending_jobs, job_spaces)

    # Modify sample_job for testing concurrency
    sample_job.max_concurrent_batches = max_jobs
    sample_job.batches = 10  # should be ignored by dispatcher in favor of pending_jobs

    # Create a sample running job
    running_job = RunningJob(
        job_data=sample_job,
        currently_running_batches=running_jobs,
        completed_batches=0,
        errored_batches=0,
        pending_batches=pending_jobs,
    )

    # Mock dispatcher methods
    dispatcher.get_job = AsyncMock()
    dispatcher.get_job.return_value = running_job
    dispatcher.dispatch_batch = AsyncMock()
    dispatcher.update_job = AsyncMock()

    # Call dispatch_as_required
    await dispatcher.dispatch_as_required(sample_job.job_id)

    # Check calls
    dispatcher.get_job.assert_called_once_with(sample_job.job_id)
    assert dispatcher.dispatch_batch.call_count == expected_dispatched_batches
    assert dispatcher.update_job.call_count == expected_dispatched_batches

    if expected_dispatched_batches == 0:
        assert not dispatcher.update_job.called
        return

    args, kwargs = dispatcher.update_job.call_args
    assert args[0] == sample_job.job_id
    updated_running_job = args[1]
    assert (
        updated_running_job.pending_batches
        == pending_jobs - expected_dispatched_batches
    )
    assert (
        updated_running_job.currently_running_batches
        == running_jobs + expected_dispatched_batches
    )

    # Job should not be deleted by the dispatcher if there are still pending batches
    assert not mock_redis_client.delete.called


@pytest.mark.asyncio
async def test_should_stop_if_job_not_found(dispatcher):
    """Should stop if job not found"""
    dispatcher.dispatch_batch = AsyncMock()
    dispatcher.get_job = AsyncMock()
    dispatcher.get_job.return_value = None

    # Call dispatch_as_required
    await dispatcher.dispatch_as_required("job_id")

    # Verify we tried to fetch the job, but found none
    dispatcher.get_job.assert_called_once_with("job_id")
    assert not dispatcher.dispatch_batch.called
