import json
import logging
from typing import Optional
import uuid

from fastapi import APIRouter

from common.models.pipeline import (
    Batch,
    JobStatusMessage,
    JobStatus,
    PipelineJob,
    JobFromAPI,
    PipelineJobType,
    PipelineHalt)
from common.rabbitmq.constants import BATCH_QUEUE, JOB_QUEUE, STATUS_QUEUE
from common.rabbitmq.connect import publish_to_queue
from dispatcher.models import RunningJob
from dispatcher.utils import redis_key
from worker.worker import WorkerException

from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
import redis as redis

from common.rabbitmq.connect import init_queues

logger = logging.getLogger(__name__)


api = APIRouter()


@api.get("/heartbeat")
def heartbeat():
    return {"status": "ok"}, 200


class DispatcherException(Exception):
    def __init__(self, detail: str, status_code: int = 500):
        """Custom exception class for dispatcher errors

        Args:
            detail (str): Description of error that occured
            status_code (int, optional): HTTP status code to report back to the client. Defaults to 500.
        """
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class Dispatcher:

    _connection: BlockingConnection
    _redis_client: redis.Redis
    _channel: BlockingChannel

    def __init__(self, connection, redis_client):
        self._connection = connection
        self._redis_client = redis_client
        self._channel = self._connection.channel()
        init_queues(self._channel)
        logger.info("Dispatcher initialized.")

    def propogate_error(self, job_id: Optional[str], e: Exception):
        """Propogare error, somehow, in the system so the user sees it - TODO!"""
        logger.error(f"Job ID {job_id} - error: {e}")
        logger.warning(
            f"TODO - Can't handle this error for job_id {job_id} as no way to hand back to the API!"
        )

    def handle_job_unpack_error(self, e: ValueError):
        self.propogate_error(None, e)
        logger.error(f"Invalid job format: {e}")
        # TODO: Pass back to api, show notificatio to uer
        # raise DispatcherException(f"Invalid job format: {e}", status_code=400)

    def handle_status_unpack_error(self, e: ValueError):
        self.propogate_error(None, e)
        # TODO: Pass back to api, show notificatio to user
        logger.error(f"Invalid status format: {e}")
        # raise DispatcherException(f"Invalid status format: {e}", status_code=400)

    def fetch_job(self) -> Optional[PipelineJob]:
        """
        Function to fetch a job from the job queue
        """
        method_frame, _, body = self._channel.basic_get(queue=JOB_QUEUE, auto_ack=True)
        if method_frame:
            try:
                job_data = json.loads(body)
                logger.info(f"Received job: {job_data}")
                logger.debug("Unpacking job data")
                return JobFromAPI(**job_data)
            except ValueError as e:
                self.handle_job_unpack_error(e)
        return None

    def dispatch_batch(self, job_id: str, job_data: Batch):
        # TODO: Add error handling
        # TODO: Different queue
        """Dispatch a single batch for the given job id"""
        try:
            logger.info(f"Dispatching batch for job {job_id}")
            self._channel = publish_to_queue(
                self._channel, BATCH_QUEUE, job_data.model_dump_json()
            )
            logger.info(f"Batch dispatched for job {job_id}")
        except Exception as e:
            self.propogate_error(job_id, e)
            # raise DispatcherException(f"Error dispatching batch: {e}")

    def dispatch_as_required(self, job_id: str):
        """Given a job id, lookup currently running jobs and dispatch until pending batches == max batches"""
        logger.info(f"Dispatching as required for job {job_id}")
        # Get the running job
        running_job = self.get_job(job_id)
        if not running_job:
            logger.error(f"Job {job_id} not found in Redis!")
            # TODO: Handle error finding jon
            self.propogate_error(job_id, ValueError("Job not found in Redis!"))
            logger.warning(f"This error for {job_id} is unhandled!")
            return

        logger.debug(f"Running job: {running_job}")

        # Stop dispatching if the job is cancelled
        if running_job.job_data == JobStatus.CANCELLED:
            logger.info(f"Job {job_id} has been CANCELLED. No batches will be dispatched.")
            return

        # How many batches can we run?
        left_batches = running_job.pending_batches
        if left_batches == 0:
            logger.info(
                f"No batches left to run for job {job_id}. All batches complete={running_job.completed_batches}, errored={running_job.errored_batches}, pending={running_job.currently_running_batches}"  # noqa
            )
            return

        # If we can run more batches, do so
        # We can dispatch up to (no. batches we can run - batches currently running), but if we have fewer than
        # that batches left, dispatch that
        batches_to_dispatch = min(
            max(
                running_job.job_data.max_concurrent_batches
                - running_job.currently_running_batches,
                0,
            ),
            left_batches,
        )
        logger.info(f"Dispatching {batches_to_dispatch} new batches for job {job_id}")
        for i in range(batches_to_dispatch):
            logger.debug(f"Dispatching batch {i+1} for job {job_id}")
            batch = Batch(
                job_id=job_id,
                batch_id=str(uuid.uuid4()),
                batch_size=running_job.job_data.batch_size,
                metrics=running_job.job_data.metrics,
                total_sample_size=running_job.job_data.total_sample_size,
            )
            self.dispatch_batch(job_id, batch)
            logger.debug(f"Updating Redis for job {job_id}")
            running_job.currently_running_batches += 1
            running_job.pending_batches = max(0, running_job.pending_batches - 1)
            running_job.status = JobStatus.RUNNING
            self.update_job(job_id, running_job)
            logger.info(
                f"Updated running job in Redis for job {job_id}, pending={running_job.pending_batches}, running={running_job.currently_running_batches}, completed={running_job.completed_batches}, errored={running_job.errored_batches}"  # noqa
            )

        logger.info(f"Dispatched {batches_to_dispatch} new batches for job {job_id}.")

    def process_new_job(self, job: PipelineJob):
        """Called when a new job is received to setup the job in redis and start processing"""
        logger.info(f"Processing job: {job}")
        logger.info(f"Preparing data to run job {job.job_id}")
        # Create object in redis
        running_job = RunningJob(
            job_data=job,
            status=JobStatus.PENDING,
            currently_running_batches=0,
            completed_batches=0,
            errored_batches=0,
            pending_batches=job.batches,
        )
        # Add to redis
        self.update_job(job.job_id, running_job)
        logger.info(f"Init data stored in Redis for job {job.job_id}")
        # Start processing job
        self.dispatch_as_required(running_job.job_data.job_id)

    def handle_job_completion(self, msg: JobStatusMessage):
        """Handle a job completion message"""
        logger.info(f"Handling job completion: {msg}")
        # Get the running job
        running_job = self.get_job(msg.job_id)
        if running_job is None:
            logger.error(f"Job {msg.job_id} not found in Redis!")
            logger.warning(f"This error for {msg.job_id} is unhandled!")
            # TODO: Handle error
            return
        # Success or error?
        match msg.status:
            case JobStatus.COMPLETED:
                running_job.completed_batches += 1
                running_job.currently_running_batches -= 1
                logger.info(f"Batch {msg.batch_id} completed!")
                # Update
                self.update_job(msg.job_id, running_job)
                # Dispatch more if required

            case JobStatus.ERRORED:
                running_job.errored_batches += 1
                running_job.currently_running_batches -= 1
                logger.error(f"Error in batch {msg.batch_id}: {msg.errorMessage}!")
                self.propogate_error(
                    msg.job_id,
                    WorkerException(
                        detail=(
                            msg.errorMessage if msg.errorMessage else "Unknown error"
                        ),
                        status_code=500,
                    ),
                )
                # TODO: Handle error
                logger.warning(
                    f"Error in batch {msg.batch_id} is unhandled! Job will not be dispatched."
                )
                # Update
                self.update_job(msg.job_id, running_job)

        # If no more pending batches, and none in progress, job is complete
        if (
            running_job.pending_batches == 0
            and running_job.currently_running_batches == 0
        ):
            logger.info(
                f"Job {msg.job_id} is complete! Finished with {running_job.errored_batches} errored batches, {running_job.completed_batches} completed batches"  # noqa
            )
            # Delete key
            self._redis_client.delete(self._get_job_redis_key(msg.job_id))
            logger.info(f"Job {msg.job_id} marked as complete & deleted")
            logger.warning(
                f"Job {msg.job_id} is complete but this is unhandled! Errored batches are not reported"
            )
        else:
            logger.info(f"Dispatching more batches for job {msg.job_id}...")
            self.dispatch_as_required(msg.job_id)

    def _get_job_redis_key(self, job_id: str) -> str:
        """Return the key to reference a job in redis"""
        return redis_key("jobs", job_id)

    def update_job(self, job_id: str, running_job: RunningJob, ttl: Optional[int] = None):
        """Update a job in redis"""
        self._redis_client.set(
            self._get_job_redis_key(job_id), running_job.model_dump_json(), ex=ttl
        )

    def get_job(self, job_id: str) -> RunningJob | None:
        """Get a job from redis"""
        job = self._redis_client.get(self._get_job_redis_key(job_id))
        if job:
            return RunningJob(**json.loads(job))
        return None

    # COnnection related logic
    def got_job(self, channel, method, properties, body: str):
        """Callback for when we get a new job"""
        try:
            job_data = json.loads(body)
            logger.info(f"Received job: {job_data}")
            logger.debug("Unpacking job data")
            job = JobFromAPI(**job_data)
            if (job.job_type == PipelineJobType.HALT_JOB):
                self.stop_job(job.job.job_id)
                return
            elif (job.job_type == PipelineJobType.START_JOB):
                self.process_new_job(job.job)
            else:
                logger.error(f"Invalid job type: {job.job_type}")
        except ValueError as e:
            self.handle_job_unpack_error(e)

    def got_status(self, channel, method, properties, body: str):
        try:
            job_data = json.loads(body)
            logger.info(f"Received status update: {job_data}")
            logger.debug("Unpacking status update")
            msg = JobStatusMessage(**job_data)
            self.handle_job_completion(msg)
        except ValueError as e:
            self.handle_status_unpack_error(e)

    def stop_job(self, job_id: str):
        """Stops a job by removing its pending batches from Redis"""
        logger.info(f"Stopping job {job_id}...")

        running_job = self.get_job(job_id)
        if not running_job:
            logger.error(f"Job {job_id} not found in Redis!")
            return

        # Mark as stopped
        running_job.status = JobStatus.CANCELLED
        # Clear pending batches
        running_job.pending_batches = 0
        self.update_job(job_id, running_job, ttl=600)
        # Store updated job in Redis with TTL, 10 mins

        logger.info(f"Job {job_id} stopped. Pending batches removed.")

    def run(self):
        """Main dispatcher loop"""
        logger.info("Dispatcher running...")

        def job_callback(channel, method, properties, body):
            self.got_job(channel, method, properties, body)

        def status_callback(channel, method, properties, body):
            self.got_status(channel, method, properties, body)

        self._channel.basic_consume(
            queue=JOB_QUEUE, on_message_callback=job_callback, auto_ack=True
        )
        self._channel.basic_consume(
            queue=STATUS_QUEUE, on_message_callback=status_callback, auto_ack=True
        )
        # Block
        self._channel.start_consuming()
