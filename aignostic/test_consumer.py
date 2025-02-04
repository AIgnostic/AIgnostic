import pika
import time

def connect_to_rabbitmq():
    for i in range(10):  # Retry up to 10 times
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq')
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"Connection failed. Retrying {i+1}/10...")
            time.sleep(3)  # Wait 3 seconds before retrying

    raise Exception("Could not connect to RabbitMQ after multiple attempts.")

def callback(ch, method, properties, body):
    print(" [x] Received and Processing (not really) %r" % body)

if __name__ == "__main__":
    print("HUARRR")
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue='job_queue')
    channel.basic_consume(queue='job_queue', on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
