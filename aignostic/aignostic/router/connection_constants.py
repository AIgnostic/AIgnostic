import socket
import pika
from fastapi import APIRouter
import time
import os

RABBIT_MQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
JOB_QUEUE = 'job_queue'
RESULT_QUEUE = 'result_queue'

def connect_to_rabbitmq():
    for i in range(10):  # Retry up to 10 times
        host = RABBIT_MQ_HOST   
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
    raise Exception("Could not connect to RabbitMQ after multiple attempts.")


connection = connect_to_rabbitmq()
print("Connection established to RabbitMQ")
channel = connection.channel()



api = APIRouter()
channel.queue_declare(queue='job_queue', durable=True)
channel.queue_declare(queue='result_queue', durable=True)


