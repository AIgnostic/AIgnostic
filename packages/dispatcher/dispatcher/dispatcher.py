import asyncio
import json
import logging
import atexit
from os import getenv
from typing import Optional

from common.models.common import Job
from common.rabbitmq.constants import JOB_QUEUE
from dispatcher.models import RunningJob
from worker.worker import WorkerException

from colorama import init
from common.redis.connect import connect_to_redis
from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
import redis.asyncio as redis

from common.rabbitmq.connect import connect_to_rabbitmq, init_queues
from dispatcher.logging.configure_logging import configure_logging

logger = logging.getLogger("dispatcher")

# gloals
connection: BlockingConnection = None
redis_client: redis.Redis = None

REDIS_HOST = getenv("REDIS_HOST", "localhost")
REDIS_PORT = getenv("REDIS_PORT", 6379)


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
        init_queues(self.channel)
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

    async def process_job(self, job: Job):
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
        await self._redis_client.set(job.user_id, running_job.json())
        logger.info(f"Init data stored in Redis for job {job.user_id}")

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
                await self.process_job(job)


async def redis_connect():
    logger.info("Connecting to Redis...")
    global redis_client
    redis_client = await connect_to_redis(f"redis://{REDIS_HOST}:{REDIS_PORT}")


def rabbitmq_connect():
    logger.info("Connecting to rabbitmq...")
    global connection
    connection = connect_to_rabbitmq()


async def startup():
    """Perform application startup actions"""
    # 1: Configure global logger so we can log thing
    configure_logging("production")
    logger.info("Dispatcher booting up...")
    rabbitmq_connect()
    await redis_connect()
    logger.info("Application startup complete.")


def cleanup():
    """Perform application cleanup actions"""
    logger.info("Shutting down...")
    if connection:
        connection.close()
        logger.info("RabbitMQ connection closed.")
    # Can't cleanup redis client because it's async
    logger.info("Application cleanup complete.")


async def main():
    """Main entry point"""
    await startup()
    logger.warning("Application logic TODO")


atexit.register(cleanup)

if __name__ == "__main__":
    asyncio.run(main())
