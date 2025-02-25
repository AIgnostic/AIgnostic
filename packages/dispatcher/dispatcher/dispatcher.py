import asyncio
import logging
from os import getenv

from pika import BlockingConnection
import redis.asyncio as redis

from common.rabbitmq.connect import connect_to_rabbitmq
from dispatcher.logging.configure_logging import configure_logging

logger = logging.getLogger("dispatcher")

# gloals
connection: BlockingConnection = None
redis_client: redis.Redis = None

REDIS_HOST = getenv("REDIS_HOST", "localhost")
REDIS_PORT = getenv("REDIS_PORT", 6379)


async def redis_connect():
    logger.info("Connecting to Redis...")
    global redis_client
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    # Attempt to connect to Redis
    await redis_client.ping()
    return redis_client


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


import atexit

atexit.register(cleanup)

if __name__ == "__main__":
    asyncio.run(main())
