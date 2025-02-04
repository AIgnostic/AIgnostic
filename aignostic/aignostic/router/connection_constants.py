import pika
from fastapi import APIRouter

RABBIT_MQ_HOST = 'localhost'

api = APIRouter()
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_MQ_HOST))
channel = connection.channel()
channel.queue_declare(queue='job_queue')