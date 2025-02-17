import os
import json
import threading
import queue
import websockets.sync.server
from pika.adapters.blocking_connection import BlockingChannel
from common.rabbitmq.connect import connect_to_rabbitmq, init_queues
from common.rabbitmq.constants import RESULT_QUEUE


class MetricsAggregator():
    def __init__(self):
        self.metrics = {}

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

    def get_aggregated_metrics(self):
        return self.metrics


RABBIT_MQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
connection = None
channel: BlockingChannel = None
connected_clients = set()  # Store multiple WebSocket clients
message_queue = queue.Queue()  # Store messages until a client connects
metrics_aggregator = MetricsAggregator()


# Connect to RabbitMQ
def connect_to_queue():
    global connection
    global channel
    connection = connect_to_rabbitmq(host=RABBIT_MQ_HOST)
    channel = connection.channel()
    init_queues(channel)

    channel.basic_consume(queue=RESULT_QUEUE, on_message_callback=on_result_fetched, auto_ack=True)

    print("Waiting for messages...")
    channel.start_consuming()  # Blocking call, waits for messages

def on_result_fetched(ch, method, properties, body):
    """Handles incoming messages and waits for at least one client before sending."""
    global connected_clients
    result_data = json.loads(body)
    print(f"Received result: {result_data}")

    metrics_aggregator.aggregate_new_batch(result_data["metric_values"], result_data["batch_size"])

    # # Format the data for frontend
    # results = []
    # if "error" in result_data:
    #     results.append({"error": result_data["error"]})
    # else:
    #     for metric, value in result_data["metric_values"].items():
    #         results.append(
    #             {
    #                 "metric": metric,
    #                 "result": value,
    #                 "legislation_results": ["Placeholder"],
    #                 "llm_model_summary": ["Placeholder"],
    #             }
    #         )

    message = json.dumps(metrics_aggregator.get_aggregated_metrics())

    # If clients exist, send immediately; otherwise, store in the queue
    if connected_clients:
        send_to_clients(message)
    else:
        print("No clients connected, storing message in queue...")
        message_queue.put(message)

def send_to_clients(message):
    """Sends messages to all connected WebSocket clients."""
    global connected_clients
    disconnected_clients = set()

    for client in connected_clients:
        try:
            client.send(message)
            print(f"Sent message to client: {message}")
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
        connected_clients.remove(websocket)  # Remove on disconnect

# Start WebSocket server in a separate thread
def start_websocket_server():
    server = websockets.sync.server.serve(websocket_handler, "0.0.0.0", 5005)
    print("WebSocket server started on ws://0.0.0.0:5005")
    server.serve_forever()  # Blocking call

if __name__ == '__main__':
    # Start WebSocket server in a separate thread
    threading.Thread(target=start_websocket_server, daemon=True).start()

    # Start RabbitMQ consumer (blocking)
    connect_to_queue()
