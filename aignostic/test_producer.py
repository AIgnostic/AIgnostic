import pika
import time
import os

def connect_to_rabbitmq():
    host = os.environ.get("RABBITMQ_HOST", "localhost")
    for i in range(10):  # Retry up to 10 times
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host, heartbeat=600)
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"Connection failed. Retrying {i+1}/10...")
            time.sleep(3)
    raise Exception("Could not connect to RabbitMQ after multiple attempts.")

connection = connect_to_rabbitmq()
channel = connection.channel()

# Ensure queue is durable
channel.queue_declare(queue='job_queue', durable=True)
print("[x] Declared durable job_queue")

# Keep sending messages instead of exiting
while True:
    message = "Hello, RabbitMQ!"
    channel.basic_publish(exchange='', routing_key='job_queue', body=message)
    print(f"[x] Sent: {message}")
