import pika
import time

def connect_to_rabbitmq():
    for i in range(10):  # Retry up to 10 times
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq', heartbeat=600)
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"Connection failed. Retrying {i+1}/10...")
            time.sleep(3)

    raise Exception("Could not connect to RabbitMQ after multiple attempts.")

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    ch.basic_ack(delivery_tag=method.delivery_tag)  # Explicit acknowledgment

while True:
    try:
        print(f"time is {time.time()}")
        connection = connect_to_rabbitmq()
        channel = connection.channel()

        # Ensure queue is durable
        channel.queue_declare(queue='job_queue', durable=True)

        channel.basic_consume(queue='job_queue', on_message_callback=callback, auto_ack=False)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except pika.exceptions.ConnectionClosedByBroker as e:
        print(f"Connection closed by broker: {e}. Reconnecting...")
        time.sleep(5)
    except pika.exceptions.AMQPConnectionError as e:
        print(f"AMQP connection error: {e}. Retrying...")
        time.sleep(5)
    except Exception as e:
        print(f"Unexpected error: {e}. Retrying...")
        time.sleep(5)
