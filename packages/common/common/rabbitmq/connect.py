import os
import pika
import socket
import time
import pika.exceptions
from pika.adapters.blocking_connection import BlockingChannel
from .constants import BATCH_QUEUE, JOB_QUEUE, RESULT_QUEUE, STATUS_QUEUE

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")


def connect_to_rabbitmq(
    host: str = os.getenv("RABBITMQ_HOST", "rabbitmq"),
    credentials: pika.PlainCredentials = pika.PlainCredentials(
        RABBITMQ_USER, RABBITMQ_PASS
    ),
    retries: int = 20,
):
    for i in range(retries):  # Retry up to 10 times
        print(f"Connecting to RabbitMQ at {host}")
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=host, heartbeat=600, credentials=credentials
                )
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


def publish_to_queue(channel: BlockingChannel, queue: str, message: str):
    try:
        # Publish the message
        channel.basic_publish(exchange="", routing_key=queue, body=message)
    except pika.exceptions.AMQPConnectionError as e:
        # If there was some connection error
        # Restablish the connection and publish the message
        print(f"Error publishing to channel: {e}")
        print("Attempting to reconnect to RabbitMQ once...")
        connection = connect_to_rabbitmq(retries=1)
        channel = connection.channel()
        init_queues(channel)
        print("Reconnected to RabbitMQ")
        channel.basic_publish(exchange="", routing_key=queue, body=message)
    except Exception as e:
        # Some unknown error occurred
        print(f"Error publishing to channel: {e}")
        if e == "Channel is closed":
            print("Attempting to reconnect to RabbitMQ once...")
            connection = connect_to_rabbitmq(retries=1)
            channel = connection.channel()
            init_queues(channel)
            print("Reconnected to RabbitMQ")
            channel.basic_publish(exchange="", routing_key=queue, body=message)
        raise e

    return channel
