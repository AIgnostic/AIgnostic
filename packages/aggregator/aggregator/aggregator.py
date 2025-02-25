import os
import json
import threading
import queue
import websockets.sync.server
from common.rabbitmq.connect import connect_to_rabbitmq, init_queues
from common.rabbitmq.constants import RESULT_QUEUE
from common.models.aggregator_models import AggregatorMessage, MessageType
from report_generation.utils import generate_report


def aggregator_metrics_completion_log():
    return AggregatorMessage(
        messageType=MessageType.METRICS_COMPLETE,
        message="Metrics processing complete - all batches successfully processed",
        statusCode=200,
        content=None
    )


def aggregator_error_log(error):
    return AggregatorMessage(
        messageType=MessageType.ERROR,
        message="Error processing metrics",
        statusCode=500,
        content=error
    )


def aggregator_final_report_log(report):
    return AggregatorMessage(
        messageType=MessageType.REPORT,
        message="Final report successfully generated",
        statusCode=200,
        content=report
    )


def aggregator_intermediate_metrics_log(metrics):
    return AggregatorMessage(
        messageType=MessageType.METRICS_INTERMEDIATE,
        message="Batch successfully processed - intermediate metrics successfully generated",
        statusCode=202,
        content={"metrics_results": metrics}
    )


class MetricsAggregator():
    def __init__(self):
        self.metrics = {}
        self.samples_processed = 0
        self.total_sample_size = 0

    def set_total_sample_size(self, total_sample_size):
        self.total_sample_size = total_sample_size

    def aggregate_new_batch(self, batch_metrics_results, batch_size):
        for metric, value in batch_metrics_results.items():
            if metric not in self.metrics:
                # First time encountering this metric, initialize with the first batch value
                self.metrics[metric] = {"value": value, "count": batch_size}
            else:
                # Update the running average incrementally
                prev_value = self.metrics[metric]["value"]
                prev_count = self.metrics[metric]["count"]

                # Compute new weighted average
                new_count = prev_count + batch_size
                self.metrics[metric]["value"] = (prev_value * prev_count + value * batch_size) / new_count
                self.metrics[metric]["count"] = new_count  # Update the total count

        self.samples_processed += batch_size

    def get_aggregated_metrics(self):
        """
            Returns the aggregated metrics as a dictionary
            i.e. { metric1: value1, metric2: value2, ... }
        """

        results = {}
        for metric, data in self.metrics.items():
            results[metric] = data["value"]
        return results


class ResultsConsumer():

    def __init__(self, host="localhost"):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        """

        self._host = host
        self._connection = None
        self._channel = None

    def connect(self):
        """Connect to RabbitMQ, returning the connection handle.

        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        self._connection = connect_to_rabbitmq(host=self._host)
        self._channel = self._connection.channel()
        init_queues(self._channel)

    def run(self, on_message_callback=None):
        """
        Run the consumer loop.

        """
        self.connect()
        try:
            self._channel.basic_consume(queue=RESULT_QUEUE, on_message_callback=on_message_callback, auto_ack=True)
            print("Waiting for messages...")
            self._channel.start_consuming()  # Blocking call, waits for messages
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """
        Cleanly shutdown the connection to RabbitMQ.

        """
        print("Closing connection...")
        self._channel.close()
        self._connection.close()


RABBIT_MQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
connected_clients = set()  # Store multiple WebSocket clients
message_queue = queue.Queue()  # Store messages until a client connects
metrics_aggregator = MetricsAggregator()


def on_result_fetched(ch, method, properties, body):
    """Handles incoming messages and waits for at least one client before sending."""
    global connected_clients
    result_data = json.loads(body)
    print(f"Received result: {result_data}")

    if (metrics_aggregator.total_sample_size == 0):
        metrics_aggregator.set_total_sample_size(result_data["total_sample_size"])

    metrics_aggregator.aggregate_new_batch(result_data["metric_values"], result_data["batch_size"])

    aggregates = metrics_aggregator.get_aggregated_metrics()

    send_to_clients(aggregator_intermediate_metrics_log(aggregates))
    print(f"{metrics_aggregator.samples_processed} / {metrics_aggregator.total_sample_size} Processed")

    if (metrics_aggregator.samples_processed == metrics_aggregator.total_sample_size):
        print("Finished processing all batches")
        # All batches have now been processed, send completion message
        metrics_aggregator.samples_processed = 0
        metrics_aggregator.metrics = {}

        send_to_clients(aggregator_metrics_completion_log())

        print("Creating and sending final report")
        # generate a report and send to the frontend
        report_json = aggregate_report(aggregates)

        send_to_clients(aggregator_final_report_log(report_json))


def aggregate_report(metrics: dict):
    """
        Generates a report to send to the frontend
        By collating the metrics, and pulling information from the report generator
    """

    report_json = generate_report(metrics, os.getenv("GOOGLE_API_KEY"))

    return report_json


def send_to_clients(message: AggregatorMessage):
    """Sends messages to all connected WebSocket clients."""
    global connected_clients
    disconnected_clients = set()

    # If clients exist, send immediately; otherwise, store in the queue
    if not connected_clients:
        print("No clients connected, storing message in queue...")
        message_queue.put(message)
        return

    for client in connected_clients:
        try:
            client.send(json.dumps(message.dict()))
            print(f"Sent message to client: {json.dumps(message.dict())}")
        except Exception as e:
            print(f"Error sending message to client: {e}")
            disconnected_clients.add(client)  # Mark client for removal

    # Remove disconnected clients
    connected_clients.difference_update(disconnected_clients)


def websocket_handler(websocket):
    """Handles WebSocket connections and sends any queued messages upon connection."""
    global connected_clients
    print("New WebSocket connection")
    connected_clients.add(websocket)

    # Send any stored messages when the first client connects
    while not message_queue.empty():
        message = message_queue.get()
        print("Sending queued message to new client")
        send_to_clients(message)

    try:
        for _ in websocket:  # Keep connection open
            pass
    except Exception as e:
        print(f"WebSocket connection closed: {e}")
    finally:
        print("Client disconnected")
        connected_clients.remove(websocket)  # Remove on disconnect


def start_websocket_server():
    server = websockets.sync.server.serve(websocket_handler, "0.0.0.0", 5005)
    print("WebSocket server started on ws://0.0.0.0:5005")
    server.serve_forever()  # Blocking call


if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Start WebSocket server in a separate thread
    threading.Thread(target=start_websocket_server, daemon=True).start()

    # Start RabbitMQ consumer (blocking)
    consumer = ResultsConsumer(RABBIT_MQ_HOST)
    consumer.run(on_result_fetched)
