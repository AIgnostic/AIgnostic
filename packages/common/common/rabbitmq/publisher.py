# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,R0205

import os
import threading
from time import sleep
from common.rabbitmq.connect import connect_to_rabbitmq
from pika import BlockingConnection, PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel


RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")


class Publisher(threading.Thread):
    """
    Long lived publisher that publishes messages to a RabbitMQ queue from
    https://github.com/pika/pika/blob/main/examples/long_running_publisher.py.
    Uses its own thread so it can respond to rabbitmq heartbeats and other
    events while the main thread is doing other things.

    Usage:
    publisher = Publisher(queue="my_queue")
    publisher.start()
    try:
        publisher.publish("Hello, World!")
        // publisher.stop()
    finally:
        publisher.join()
    """

    daemon = True
    is_running = True
    name = "Publisher"

    queue: str
    connection: BlockingConnection
    channel: BlockingChannel

    def __init__(
        self,
        queue: str,
        name: str = "Publisher",
        host: str = os.getenv("RABBITMQ_HOST", "rabbitmq"),
        credentials: PlainCredentials = PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        retries: int = 10,
        *args,
        **kwargs,
    ):
        """Create a publisher for a channel that lives on its own thread and publishes messages to a RabbitMQ queue

        Args:
            queue (str): Queue name to publish to (will be declared durable if it doesn't exist)
            name (str, optional): Name of this publisher.
                Defaults to "Publisher".
            host (str, optional): Hostname to connect to.
            Defaults to os.getenv("RABBITMQ_HOST", "rabbitmq").
            credentials (PlainCredentials, optional): Creds to connect with.
            Defaults to PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS).
            retries (int, optional): Number of times to retry connecting
                to RabbitMQ. Defaults to 10.
        """
        super().__init__(*args, **kwargs)
        self.daemon = True
        self.is_running = True
        self.name = name
        self.queue = queue

        self.connection = connect_to_rabbitmq(
            host=host, credentials=credentials, retries=retries
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)

    def on_tick(self):
        self.connection.process_data_events(time_limit=1)

    def run(self):
        while self.is_running:
            self.on_tick()

    def _publish(self, message):
        self.channel.basic_publish("", self.queue, body=message.encode())

    def publish(self, message):
        self.connection.add_callback_threadsafe(lambda: self._publish(message))

    def stop(self):
        print("Stopping...")
        self.is_running = False
        # Wait until all the data events have been processed
        self.connection.process_data_events(time_limit=1)
        if self.connection.is_open:
            self.connection.close()
        print("Stopped")


if __name__ == "__main__":
    publisher = Publisher()
    publisher.start()
    try:
        for i in range(9999):
            msg = f"Message {i}"
            print(f"Publishing: {msg!r}")
            publisher.publish(msg)
            sleep(1)
    except KeyboardInterrupt:
        publisher.stop()
    finally:
        publisher.join()
