import pika
import socket
import time
from pika.adapters.blocking_connection import BlockingChannel
from .constants import BATCH_QUEUE, JOB_QUEUE, RESULT_QUEUE, STATUS_QUEUE


def connect_to_rabbitmq(
    host: str = "localhost",
    retries: int = 20,
):
    for i in range(retries):  # Retry up to 10 times
        print(f"Connecting to RabbitMQ at {host}")
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host, heartbeat=600)
            )
            return connection
        except (pika.exceptions.AMQPConnectionError, socket.gaierror) as e:
            print(f"Connection failed due to {e}. Retrying {i+1}/{retries}...")
            print(f"Connection failed. Retrying {i+1}/{retries}...")
            time.sleep(3)
    raise Exception(f"Could not connect to RabbitMQ after {retries} attempts.")


def init_queues(channel: BlockingChannel):
    channel.queue_declare(queue=JOB_QUEUE, durable=True)
    channel.queue_declare(queue=RESULT_QUEUE, durable=True)
    channel.queue_declare(queue=BATCH_QUEUE, durable=True)
    channel.queue_declare(queue=STATUS_QUEUE, durable=True)
