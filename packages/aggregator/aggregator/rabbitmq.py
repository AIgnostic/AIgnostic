import os
from common.rabbitmq.connect import connect_to_rabbitmq, init_queues
from pika.adapters.blocking_connection import BlockingChannel

connection = None
channel: BlockingChannel = None

RABBIT_MQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")


def get_channel():
    return channel


def fastapi_connect_rabbitmq():
    global connection
    global channel
    connection = connect_to_rabbitmq(host=RABBIT_MQ_HOST, retries=20)
    channel = connection.channel()
    init_queues(channel)
    print("Connection established to RabbitMQ")
    return (channel, connection)
