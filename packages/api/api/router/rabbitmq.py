import os
from common.rabbitmq.constants import JOB_QUEUE
from common.rabbitmq.publisher import Publisher

publisher: Publisher = None
RABBIT_MQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")


def get_jobs_publisher():
    return publisher


def create_publisher():
    global publisher
    publisher = Publisher(queue=JOB_QUEUE)
    print("Connection established to RabbitMQ")
    return publisher
