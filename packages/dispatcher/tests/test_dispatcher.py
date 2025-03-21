import json
from typing import List
import uuid

from common.models.pipeline import (
    Batch,
    JobStatusMessage,
    JobStatus,
    MetricCalculationJob,
    PipelineJob,
)
from common.rabbitmq.constants import JOB_QUEUE, STATUS_QUEUE
import pytest
from unittest.mock import MagicMock
from dispatcher.dispatcher import Dispatcher, DispatcherException, JobFromAPI, PipelineJobType
from dispatcher.models import RunningJob
from metrics.models import TaskType


@pytest.fixture
def mock_redis_client():
    """Fixture for creating a mock Redis client."""
    return MagicMock()


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
    return JobFromAPI(
            job_type=PipelineJobType.START_JOB,
            job=PipelineJob(
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
                    model_type=TaskType.BINARY_CLASSIFICATION,
                ),
            ),
        )


def test_dispatcher_exception_has_detail_and_status_code():
    """Should have a detail and status code"""
    detail = "This is a test"
    status_code = 400
    exception = DispatcherException(detail, status_code)
    assert exception.detail == detail
    assert exception.status_code == status_code


def test_should_propogate_dispatcher_exception_if_malformed_job(
    dispatcher, mock_connection
):
    """Should propogate an exception if the job is malformed"""
    # Mock the channel's basic_get result
    mock_connection.channel.return_value.basic_get.return_value = (
        True,
        None,
        "malfomed job",
    )
    dispatcher.propogate_error = MagicMock()

    dispatcher.fetch_job()
    dispatcher.propogate_error.assert_called_once()


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


def test_should_load_job_to_redis_and_dispatch(
    dispatcher, mock_redis_client, sample_job
):
    """Should load a job onto redis and start dispatching"""
    dispatcher.dispatch_as_required = MagicMock()

    # Call process_new_job with the sample job
    dispatcher.process_new_job(sample_job.job)

    # Check if the job was added to Redis
    mock_redis_client.set.assert_called_once()
    args, kwargs = mock_redis_client.set.call_args
    args: List[str]

    running_job = RunningJob(
        job_data=sample_job.job,
        status=JobStatus.PENDING,
        currently_running_batches=0,
        completed_batches=0,
        errored_batches=0,
        pending_batches=10,
    )
    assert str(sample_job.job.job_id) in args[0]
    assert args[1] == running_job.model_dump_json()
    assert dispatcher.dispatch_as_required.called


def test_dispatch_batch_dispatches(mock_connection, sample_job):
    """Should dispatch a single batch"""
    channel_mock = MagicMock()
    mock_connection.channel.return_value = channel_mock
    channel_mock.basic_publish = MagicMock()

    dispatcher = Dispatcher(mock_connection, mock_redis_client)

    # Create a sample batch
    batch = Batch(
        job_id=str(sample_job.job.job_id),
        batch_id=str(uuid.uuid4()),
        batch_size=10,
        metrics=sample_job.job.metrics,
        total_sample_size=100,
    )

    # Call dispatch_batch with the job_id and the batch
    dispatcher.dispatch_batch(sample_job.job.job_id, batch)

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
def test_should_dispatch_new_batches_as_needed(
    dispatcher, pending_jobs, max_jobs, running_jobs, mock_redis_client, sample_job
):
    """Should dispatch new batches as required - until pending == max"""
    job_spaces = max(0, max_jobs - running_jobs)
    expected_dispatched_batches = min(pending_jobs, job_spaces)

    # Modify sample_job for testing concurrency
    sample_job.job.max_concurrent_batches = max_jobs
    sample_job.job.batches = 10  # should be ignored by dispatcher in favor of pending_jobs

    # Create a sample running job
    running_job = RunningJob(
        job_data=sample_job.job,
        status=JobStatus.RUNNING,
        currently_running_batches=running_jobs,
        completed_batches=0,
        errored_batches=0,
        pending_batches=pending_jobs,
    )

    # Mock dispatcher methods
    dispatcher.get_job = MagicMock()
    dispatcher.get_job.return_value = running_job
    dispatcher.dispatch_batch = MagicMock()
    dispatcher.update_job = MagicMock()

    # Call dispatch_as_required
    dispatcher.dispatch_as_required(sample_job.job.job_id)

    # Check calls
    dispatcher.get_job.assert_called_once_with(sample_job.job.job_id)
    assert dispatcher.dispatch_batch.call_count == expected_dispatched_batches
    assert dispatcher.update_job.call_count == expected_dispatched_batches

    if expected_dispatched_batches == 0:
        assert not dispatcher.update_job.called
        return

    args, kwargs = dispatcher.update_job.call_args
    assert args[0] == sample_job.job.job_id
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


def test_should_stop_if_job_not_found(dispatcher):
    """Should stop if job not found"""
    dispatcher.dispatch_batch = MagicMock()
    dispatcher.get_job = MagicMock()
    dispatcher.get_job.return_value = None

    # Call dispatch_as_required
    dispatcher.dispatch_as_required("job_id")

    # Verify we tried to fetch the job, but found none
    dispatcher.get_job.assert_called_once_with("job_id")
    assert not dispatcher.dispatch_batch.called


def test_get_job_should_get_job(dispatcher, mock_redis_client, sample_job):
    """Should get a job from Redis"""

    running_job = RunningJob(
        job_data=sample_job.job,
        status=JobStatus.PENDING,
        currently_running_batches=0,
        completed_batches=0,
        errored_batches=0,
        pending_batches=10,
    )

    mock_redis_client.get.return_value = running_job.model_dump_json()

    # Call get_job
    res = dispatcher.get_job("job_id")

    # Verify that the job was fetched from Redis
    mock_redis_client.get.assert_called_once_with(
        dispatcher._get_job_redis_key("job_id")
    )
    assert res == running_job


def test_should_return_none_if_no_job_get_job(dispatcher, mock_redis_client):
    """Should return None if no job found in Redis"""

    mock_redis_client.get.return_value = None

    # Call get_job
    res = dispatcher.get_job("job_id")

    # Verify that the job was fetched from Redis
    mock_redis_client.get.assert_called_once_with(
        dispatcher._get_job_redis_key("job_id")
    )
    assert res is None


# Handle job complete
def test_job_complete_bad_input(dispatcher, mock_redis_client):
    """If the job is not found, should log an error and return"""
    dispatcher.get_job = MagicMock()
    dispatcher.get_job.return_value = None

    # Call handle_job_completion
    dispatcher.handle_job_completion(
        JobStatusMessage(
            job_id="job_id",
            batch_id="batch_id",
            status=JobStatus.COMPLETED,
        )
    )

    # Verify that the job was fetched from Redis
    dispatcher.get_job.assert_called_once_with("job_id")
    assert not mock_redis_client.delete.called


# If completed job, should update the job to inc complete, dec pending and dispatch more
def test_job_complete_completed(dispatcher, mock_redis_client, sample_job):
    """If the job is completed, should update the job to inc complete, dec running and dispatch more"""
    dispatcher.get_job = MagicMock()
    dispatcher.get_job.return_value = RunningJob(
        job_data=sample_job.job,
        status=JobStatus.RUNNING,
        currently_running_batches=1,
        completed_batches=0,
        errored_batches=0,
        pending_batches=10,
    )

    dispatcher.dispatch_as_required = MagicMock()

    # Call handle_job_completion
    dispatcher.handle_job_completion(
        JobStatusMessage(
            job_id=str(sample_job.job.job_id),
            batch_id="batch_id",
            status=JobStatus.COMPLETED,
        )
    )

    # Verify that the job was fetched from Redis
    dispatcher.get_job.assert_called_once_with(str(sample_job.job.job_id))

    # Verify that the job was updated correctly - one less currently running, one more completed
    mock_redis_client.set.assert_called_once()
    args, kwargs = mock_redis_client.set.call_args
    assert args[0] == dispatcher._get_job_redis_key(str(sample_job.job.job_id))
    updated_running_job = RunningJob(**json.loads(args[1]))
    assert updated_running_job.completed_batches == 1
    assert updated_running_job.pending_batches == 10
    assert updated_running_job.currently_running_batches == 0

    # Verify that more batches were dispatched
    dispatcher.dispatch_as_required.assert_called_once_with(str(sample_job.job.job_id))


def test_job_error_handled(dispatcher, mock_redis_client, sample_job):
    """If the job is errored, should update the job to inc errored and log an error"""
    dispatcher.get_job = MagicMock()
    dispatcher.get_job.return_value = RunningJob(
        job_data=sample_job.job,
        status=JobStatus.RUNNING,
        currently_running_batches=1,
        completed_batches=0,
        errored_batches=0,
        pending_batches=10,
    )

    dispatcher.dispatch_as_required = MagicMock()

    # Call handle_job_completion
    dispatcher.handle_job_completion(
        JobStatusMessage(
            job_id=str(sample_job.job.job_id),
            batch_id="batch_id",
            status=JobStatus.ERRORED,
            errorMessage="Error message",
        )
    )

    # Verify that the job was fetched from Redis
    dispatcher.get_job.assert_called_once_with(str(sample_job.job.job_id))

    # Verify that the job was updated correctly - one more errored
    mock_redis_client.set.assert_called_once()
    args, kwargs = mock_redis_client.set.call_args
    assert args[0] == dispatcher._get_job_redis_key(str(sample_job.job.job_id))
    updated_running_job = RunningJob(**json.loads(args[1]))
    assert updated_running_job.errored_batches == 1
    assert updated_running_job.pending_batches == 10
    assert updated_running_job.currently_running_batches == 0

    # Verify that no more batches were dispatched
    dispatcher.dispatch_as_required.assert_called_once_with(str(sample_job.job.job_id))
    assert not mock_redis_client.delete.called


def test_should_delete_on_last_batch(dispatcher, mock_redis_client, sample_job):
    """If no more pending batches, and none in progress, job is complete"""
    dispatcher.get_job = MagicMock()
    dispatcher.get_job.return_value = RunningJob(
        job_data=sample_job.job,
        status=JobStatus.RUNNING,
        currently_running_batches=2,  # 2: Only the second one should cause completion
        completed_batches=9,
        errored_batches=1,
        pending_batches=0,
    )
    dispatcher.dispatch_as_required = MagicMock()

    # Call handle_job_completion
    dispatcher.handle_job_completion(
        JobStatusMessage(
            job_id=str(sample_job.job.job_id),
            batch_id="batch_id",
            status=JobStatus.COMPLETED,
        )
    )

    # Verify that the job was fetched from Redis
    dispatcher.get_job.assert_called_with(str(sample_job.job.job_id))

    # Verify not deleted yet
    assert not mock_redis_client.delete.called

    # Call again
    dispatcher.handle_job_completion(
        JobStatusMessage(
            job_id=str(sample_job.job.job_id),
            batch_id="batch_id",
            status=JobStatus.COMPLETED,
        )
    )

    # Verify that the job was fetched from Redis
    dispatcher.get_job.assert_called_with(str(sample_job.job.job_id))

    # Verify that the job was deleted
    mock_redis_client.delete.assert_called_once_with(
        dispatcher._get_job_redis_key(str(sample_job.job.job_id))
    )

    # Verify that only one job was dispatched
    dispatcher.dispatch_as_required.assert_called_once()


def test_should_propogate_error_if_dispatch_fails(
    dispatcher, mock_connection, sample_job
):
    dispatcher.propogate_error = MagicMock()
    # Make basic_publish throw error
    mock_connection.channel.return_value.basic_publish.side_effect = Exception()

    # Call dispatch_batch with the job_id and the batch
    dispatcher.dispatch_batch(
        sample_job.job.job_id,
        Batch(
            job_id=str(sample_job.job.job_id),
            batch_id=str(uuid.uuid4()),
            batch_size=10,
            metrics=sample_job.job.metrics,
            total_sample_size=100,
        ),
    )

    # Should prop
    dispatcher.propogate_error.assert_called_once()


def test_got_status_update_should_process(dispatcher, sample_job):
    dispatcher.handle_job_completion = MagicMock()
    update = JobStatusMessage(
        job_id=str(sample_job.job.job_id),
        batch_id="batch_id",
        status=JobStatus.COMPLETED,
    )
    # Call got_job
    dispatcher.got_status(None, None, None, update.model_dump_json())
    dispatcher.handle_job_completion.assert_called_once_with(update)


def test_status_unpack_error_propogates(dispatcher, sample_job):
    dispatcher.propogate_error = MagicMock()
    # Call got_status
    dispatcher.got_status(None, None, None, "jinvalidjsonkdqw{}}")

    # Should prop
    dispatcher.propogate_error.assert_called_once()


def test_got_job_should_process(dispatcher, sample_job):
    dispatcher.process_new_job = MagicMock()
    # Call got_job
    dispatcher.got_job(None, None, None, sample_job.model_dump_json())
    dispatcher.process_new_job.assert_called_once_with(sample_job.job)


def test_job_unpack_error_propogates(dispatcher, sample_job):
    dispatcher.propogate_error = MagicMock()
    # Call got_status
    dispatcher.got_job(None, None, None, "jinvalidjsonkdqw{}}")

    # Should prop
    dispatcher.propogate_error.assert_called_once()


def test_run_should_queue_for_job_and_status(dispatcher, mock_connection):
    # Run should call basic_consume twice, once for JOB_QEUE and the other for STATUS_QUEUE
    mock_channel = mock_connection.channel.return_value
    dispatcher.run()
    assert mock_channel.basic_consume.call_count == 2
    assert mock_channel.basic_consume.call_args_list[0][1]["queue"] == JOB_QUEUE
    assert mock_channel.basic_consume.call_args_list[1][1]["queue"] == STATUS_QUEUE
    # Was start_consuming called?
    assert mock_channel.start_consuming.called
