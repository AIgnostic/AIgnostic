import pika
import socket
import time
from pika.adapters.blocking_connection import BlockingChannel


def connect_to_rabbitmq(
    host: str = "localhost",
    retries: int = 10,
):
    for i in range(retries):  # Retry up to 10 times
        print(f"Connecting to RabbitMQ at {host}")
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host, heartbeat=600)
            )
            return connection
        except (pika.exceptions.AMQPConnectionError, socket.gaierror) as e:
            print(f"Connection failed due to {e}. Retrying {i+1}/10...")
            print(f"Connection failed. Retrying {i+1}/10...")
            time.sleep(3)
    raise Exception(f"Could not connect to RabbitMQ after {retries} attempts.")


def init_queues(channel: BlockingChannel):
    channel.queue_declare(queue="job_queue", durable=True)
    channel.queue_declare(queue="result_queue", durable=True)
