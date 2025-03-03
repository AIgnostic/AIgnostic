import os
import json
import threading
import queue
import websockets.sync.server
from common.rabbitmq.connect import connect_to_rabbitmq, init_queues
from common.rabbitmq.constants import RESULT_QUEUE
from common.models.aggregator_models import AggregatorMessage, MessageType
from report_generation.utils import generate_report
import time


def aggregator_metrics_completion_log():
    return AggregatorMessage(
        messageType=MessageType.METRICS_COMPLETE,
        message="Metrics processing complete - all batches successfully processed",
        statusCode=200,
        content=None,
    )


def aggregator_error_log(error):
    return AggregatorMessage(
        messageType=MessageType.ERROR,
        message="Error processing metrics",
        statusCode=500,
        content=error,
    )


def aggregator_final_report_log(report):
    return AggregatorMessage(
        messageType=MessageType.REPORT,
        message="Final report successfully generated",
        statusCode=200,
        content=report,
    )


def aggregator_intermediate_metrics_log(metrics):
    return AggregatorMessage(
        messageType=MessageType.METRICS_INTERMEDIATE,
        message="Batch successfully processed - intermediate metrics successfully generated",
        statusCode=202,
        content={"metrics_results": metrics},
    )


class MetricsAggregator:
    def __init__(self):
        self.metrics = {}
        self.samples_processed = 0
        self.total_sample_size = 0

    def set_total_sample_size(self, total_sample_size):
        self.total_sample_size = total_sample_size

    def aggregate_new_batch(self, batch_metrics_results, batch_size):
        for metric, metric_value_obj in batch_metrics_results.items():
            if metric not in self.metrics:
                # First time encountering this metric, initialize with the first batch value
                self.metrics[metric] = {
                    "value": metric_value_obj["computed_value"],
                    "ideal_value": metric_value_obj["ideal_value"],
                    "range": metric_value_obj["range"],
                    "count": batch_size
                }
            else:
                # Update the running average incrementally
                prev_value = self.metrics[metric]["value"]
                prev_count = self.metrics[metric]["count"]

                # Compute new weighted average
                new_count = prev_count + batch_size
                new_value = (prev_value * prev_count + metric_value_obj["computed_value"] * batch_size) / new_count
                self.metrics[metric]["value"] = new_value
                self.metrics[metric]["count"] = new_count  # Update the total count

        self.samples_processed += batch_size

    def get_aggregated_metrics(self):
        """
        Returns the aggregated metrics as a dictionary.
        Example:
        {
            "metric1": {
                "value": value1,
                "ideal_value": ideal_value1,
                "range": range1
            },
            "metric2": {
                "value": value2,
                "ideal_value": ideal_value2,
                "range": range2
            },
            ...
        }
        """
        results = {}
        for metric, data in self.metrics.items():
            results[metric] = {
                "value": data["value"],
                "ideal_value": data["ideal_value"],
                "range": data["range"]
            }
        return results


class ResultsConsumer:

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
            self._channel.basic_consume(
                queue=RESULT_QUEUE,
                on_message_callback=on_message_callback,
                auto_ack=True,
            )
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
# Store multiple WebSocket clients
connected_clients = set()
# Store messages until a client connects
message_queue = queue.Queue()
# user_id -> MetricsAggregator
user_aggregators: dict = {}


def on_result_fetched(ch, method, properties, body):
    result_data = json.loads(body)
    user_id = result_data["user_id"]
    print(f"Received result for user {user_id}: {result_data}")

    if result_data["user_defined_metrics"] is not None:
        print(f"User-defined metrics received for user {user_id}: {result_data['user_defined_metrics']}")

    # ensure a metricsaffregator exists for the user
    if user_id not in user_aggregators:
        user_aggregators[user_id] = MetricsAggregator()

    aggregator: MetricsAggregator = user_aggregators[user_id]

    if aggregator.total_sample_size == 0:
        aggregator.set_total_sample_size(result_data["total_sample_size"])

    batch_metrics = result_data["metric_values"]
    if result_data["user_defined_metrics"]:
        for metric, metric_info in result_data["user_defined_metrics"].items():
            batch_metrics[metric] = metric_info["result"]

    aggregator.aggregate_new_batch(result_data["metric_values"], result_data["batch_size"])

    aggregates = aggregator.get_aggregated_metrics()
    # send the intermediate metrics to the user
    manager.send_to_user(user_id, aggregator_intermediate_metrics_log(aggregates))
    print(f"{aggregator.samples_processed} / {aggregator.total_sample_size} Processed for user {user_id}")

    # if all batches have been processed, send final result

    if aggregator.samples_processed == aggregator.total_sample_size:
        print(f"Finished processing all batches for user {user_id}")

        # send completion message
        manager.send_to_user(user_id, aggregator_metrics_completion_log())

        report_thread = threading.Thread(target=generate_and_send_report, args=(user_id, aggregates, aggregator))
        report_thread.start()

        # cleanup completed aggregator
        del user_aggregators[user_id]


def get_api_key():
    # if GOOGLE_API_KEY_FILE is set, read the key from the file
    if os.getenv("GOOGLE_API_KEY_FILE"):
        with open(os.getenv("GOOGLE_API_KEY_FILE")) as f:
            return f.read().strip()
    return os.getenv("GOOGLE_API_KEY")


def aggregator_generate_report(aggregates, aggregator):
    """Generates a report based on the aggregated metrics."""
    report_properties_section = generate_report(aggregates, os.getenv("GOOGLE_API_KEY"))
    report_info_section = {
        # TODO: Update with codecarbon info and calls to model from metrics
        "calls_to_model": aggregator.total_sample_size,
        "date": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


    }
    report_json = {"properties": report_properties_section, "info": report_info_section}
    return report_json


def generate_and_send_report(user_id, aggregates, aggregator):
    """Generates the report and sends it without blocking the main process."""
    try:
        report_json = aggregator_generate_report(aggregates, aggregator)
        manager.send_to_user(user_id, aggregator_final_report_log(report_json))
    except Exception as e:
        print(f"Error generating report for user {user_id}: {e}")
        manager.send_to_user(user_id, aggregator_error_log(str(e)))


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
            client.send(message.model_dump_json())
            print(f"Sent message to client: {message.model_dump_json()}")
        except Exception as e:
            print(f"Error sending message to client: {e}")
            disconnected_clients.add(client)  # Mark client for removal

    # Remove disconnected clients
    connected_clients.difference_update(disconnected_clients)


class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    def connect(self, user_id, websocket):
        """Stores a Websocket connection for a specific user"""
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id):
        """Removes a Websocket connection for a specific user"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    def send_to_user(self, user_id, message):
        """Sends a message to the correct user."""

        if user_id in self.active_connections:
            print(f"Sending message to user {user_id}")
            websocket = self.active_connections[user_id]
            try:
                websocket.send(json.dumps(message.dict()))
                print(f"Sent message to user {user_id}: {json.dumps(message.dict())}")
            except Exception as e:
                print(f"Error sending message to user {user_id}: {e}")
                self.disconnect(user_id)
        else:
            print(f"User not connected: {user_id}")
            print(f"Active connections {self.active_connections}")


manager = ConnectionManager()


def websocket_handler(websocket):
    """Handles Websocket connections and assigns them to users"""
    try:
        user_id = websocket.recv()
        print(f"User {user_id} connected via websocket")

        # register this user
        manager.connect(user_id, websocket)

        for _ in websocket:
            # keep connection open
            pass
    except Exception as e:
        print(f"Websocket connection closed: {e}")
    finally:
        print(f"User {user_id} disconnected")
        manager.disconnect(user_id)


def start_websocket_server():
    server = websockets.sync.server.serve(websocket_handler, "0.0.0.0", 5005)
    print("WebSocket server started on ws://0.0.0.0:5005")
    server.serve_forever()  # Blocking call


if __name__ == "__main__":
    # Load environment variables

    from dotenv import load_dotenv

    load_dotenv()

    # Start WebSocket server in a separate thread
    threading.Thread(target=start_websocket_server, daemon=True).start()

    # Start RabbitMQ consumer (blocking)
    consumer = ResultsConsumer(RABBIT_MQ_HOST)
    consumer.run(on_result_fetched)
