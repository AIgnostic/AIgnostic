import pika
from fastapi import APIRouter

RABBIT_MQ_HOST = 'localhost'
JOB_QUEUE = 'job_queue'

api = APIRouter()
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_MQ_HOST))
channel = connection.channel()
channel.queue_declare(queue='job_queue')
