import asyncio
import json
import logging
import atexit
from os import getenv
from typing import Optional, Tuple

from dispatcher.dispatcher import Dispatcher

from common.redis.connect import connect_to_redis
from pika import BlockingConnection
import redis.asyncio as redis

from common.rabbitmq.connect import connect_to_rabbitmq, init_queues
from dispatcher.logging.configure_logging import configure_logging

logger = logging.getLogger("dispatcher")

# gloals
REDIS_HOST = getenv("REDIS_HOST", "localhost")
REDIS_PORT = getenv("REDIS_PORT", 6379)


async def redis_connect() -> redis.Redis:
    logger.info("Connecting to Redis...")
    global redis_client
    redis_client = await connect_to_redis(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    logger.info("Connected to Redis.")
    return redis_client


def rabbitmq_connect() -> BlockingConnection:
    logger.info("Connecting to rabbitmq...")
    return connect_to_rabbitmq()


async def startup() -> Tuple[BlockingConnection, redis.Redis]:
    """Perform application startup actions"""
    # 1: Configure global logger so we can log thing
    configure_logging("production")
    logger.info("Dispatcher booting up...")
    connection = rabbitmq_connect()
    redis = await redis_connect()
    logger.info("Application startup complete.")
    return connection, redis


def cleanup(connection: Optional[BlockingConnection] = None):
    """Perform application cleanup actions"""
    logger.info("Shutting down...")
    if connection:
        connection.close()
        logger.info("RabbitMQ connection closed.")
    # Can't cleanup redis client because it's async
    logger.info("Application cleanup complete.")


async def main():
    """Main entry point"""
    logger.warning("Starting dispatcher...")
    connection, redis = await startup()
    dispatcher = Dispatcher(connection, redis)
    await dispatcher.run()


atexit.register(cleanup)

if __name__ == "__main__":
    asyncio.run(main())
