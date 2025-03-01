import json
import logging
from typing import Optional

from common.models.common import Job
from common.rabbitmq.constants import JOB_QUEUE
from dispatcher.models import RunningJob
from dispatcher.utils import redis_key
from worker.worker import WorkerException

from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
import redis.asyncio as redis

from common.rabbitmq.connect import init_queues

logger = logging.getLogger(__name__)


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

    def handle_job_unpack_error(self, e: ValueError):
        logger.error(f"Invalid job format: {e}")
        logger.error("Can't handle this error as no way to hand back to the API!")
        # TODO: Pass back to api, show notificatio to uer
        raise DispatcherException(f"Invalid job format: {e}", status_code=400)

    def fetch_job(self) -> Optional[Job]:
        """
        Function to fetch a job from the job queue
        """
        method_frame, header_frame, body = self._channel.basic_get(
            queue=JOB_QUEUE, auto_ack=True
        )
        if method_frame:
            job_data = json.loads(body)
            logger.info(f"Received job: {job_data}")
            try:
                logger.debug("Unpacking job data")
                return Job(**job_data)
            except ValueError as e:
                self.handle_job_unpack_error(e)
        return None

    async def dispatch_as_required(self, user_id: str):
        """Given a user id, lookup currently running jobs and dispatch as required"""
        logger.info(f"Dispatching as required for job {user_id}")
        # Get the running job
        running_job = await self._redis_client.get(self._get_job_redis_key(user_id))
        if not running_job:
            logger.error(f"Job {user_id} not found in Redis!")
            # TODO: Handle error finding jon
            logger.warning(f"This error for {user_id} is unhandled!")
            return
        running_job = RunningJob(**json.loads(running_job))
        logger.debug(f"Running job: {running_job}")
        # How many batches can we run?
        left_batches = running_job.pending_batches
        if left_batches == 0:
            logger.info(
                f"No batches left to run for job {user_id} - regarding as complete"
            )
            # TODO: Handle completion & report errored batches
            # Delete key
            await self._redis_client.delete(self._get_job_redis_key(user_id))
            logger.info(f"Job {user_id} marked as complete & deleted")
            logger.warning(
                f"Job {user_id} is complete but this is unhandled! Erroed batches are not reproted"
            )
            return
        # If we can run more batches, do so
        # We can dispatch up to (no. batches we can run - batches currently running), but if we have fewer than that batches left, dispatch that
        batches_to_dispatch = min(
            running_job.max_concurrent_batches - running_job.currently_running_batches,
            left_batches,
        )
        logger.info(f"Dispatching {batches_to_dispatch} new batches for job {user_id}")
        # Dispatch batches
        logger.warning("TODO: Dispatch batches")
        # Update running job
        running_job.currently_running_batches += batches_to_dispatch
        running_job.pending_batches -= batches_to_dispatch
        # Update redis
        await self._redis_client.set(
            self._get_job_redis_key(user_id), running_job.model_dump_json()
        )
        logger.info(
            f"Updated running job in Redis for job {user_id}, pending={running_job.pending_batches}, running={running_job.currently_running_batches}, completed={running_job.completed_batches}, errored={running_job.errored_batches}"
        )

    def _get_job_redis_key(self, user_id: str) -> str:
        return redis_key("jobs", user_id)

    async def process_new_job(self, job: Job):
        logger.info(f"Processing job: {job}")
        logger.info(f"Preparing data to run job {job.user_id}")
        # Create object in redis
        running_job = RunningJob(
            job_data=job,
            user_id=job.user_id,
            max_concurrent_batches=job.max_concurrenct_batches,
            currently_running_batches=0,
            completed_batches=0,
            errored_batches=0,
            pending_batches=job.total_sample_size,
        )
        # Add to redis
        await self._redis_client.set(
            self._get_job_redis_key(job.user_id), running_job.model_dump_json()
        )
        logger.info(f"Init data stored in Redis for job {job.user_id}")
        # Start processing job
        await self.dispatch_as_required(running_job.user_id)

    async def run(self):
        logger.info("Dispatcher running...")
        while True:
            try:
                job = self.fetch_job()
            except WorkerException as e:
                logger.error(f"Error unpacking job: {e}")
                logger.error("Waiting for next job...")
                continue

            if job:
                await self.process_new_job(job)
