import json
import logging
from typing import Optional

from common.models.common import Job
from common.rabbitmq.constants import JOB_QUEUE
from dispatcher.models import RunningJob
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
        )
        # Add to redis
        await self._redis_client.set(job.user_id, running_job.model_dump_json())
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
