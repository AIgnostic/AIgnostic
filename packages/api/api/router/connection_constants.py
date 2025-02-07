from common.rabbitmq.connect import connect_to_rabbitmq
from fastapi import APIRouter
import os

RABBIT_MQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")

# connection = connect_to_rabbitmq(
#     host=RABBIT_MQ_HOST,
#     retries=10,
# )
# print("Connection established to RabbitMQ")
# channel = connection.channel()

# api = APIRouter()
# channel.queue_declare(queue="job_queue", durable=True)
# channel.queue_declare(queue="result_queue", durable=True)
