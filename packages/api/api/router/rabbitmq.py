import os
from common.rabbitmq.connect import connect_to_rabbitmq, init_queues

connection = None
channel = None

RABBIT_MQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")


def get_channel():
    return channel


def ack_cb(method_frame):
    print(f"Got Pika ack: {method_frame}")


def fastapi_connect_rabbitmq():
    global connection
    global channel
    connection = connect_to_rabbitmq(host=RABBIT_MQ_HOST, retries=10)
    channel = connection.channel()
    channel.confirm_delivery()
    init_queues(channel)
    print("Connection established to RabbitMQ")
    return channel
