import os
import asyncio
import json
import websockets
from fastapi import FastAPI
from pika.adapters.blocking_connection import BlockingChannel
from common.rabbitmq.connect import connect_to_rabbitmq, init_queues
from common.rabbitmq.constants import RESULT_QUEUE, AGGREGATES_QUEUE

RABBIT_MQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
connection = None
channel: BlockingChannel = None
connected_clients = set()

# Connect to RabbitMQ
async def connect_to_queue():
    global connection
    global channel
    connection = connect_to_rabbitmq(host=RABBIT_MQ_HOST)
    channel = connection.channel()
    init_queues(channel)

    channel.basic_consume(queue=RESULT_QUEUE, on_message_callback=on_result_fetched, auto_ack=True)

    # Start consuming messages in the current event loop
    print("Waiting for messages...")
    await asyncio.to_thread(channel.start_consuming)

def on_result_fetched(ch, method, properties, body):
    result_data = json.loads(body)
    print(f"Received result: {result_data}")

    # TEMPORARY
    # Format the data into the format the frontend expects
    results = []
    if "error" in result_data:
        results.append({"error": result_data["error"]})
    else:
        for metric, value in result_data["metric_values"].items():
            results.append(
                {
                    "metric": metric,
                    "result": value,
                    "legislation_results": ["Placeholder"],
                    "llm_model_summary": ["Placeholder"],
                }
            )

    # Send the result to all connected clients
    asyncio.create_task(async_send_to_clients(json.dumps(results)))

# Function to send data to all WebSocket clients
async def async_send_to_clients(message):
    for client in connected_clients:
        try:
            await client.send(message)
            print(f"Sent message to client: {message}")
        except Exception as e:
            print(f"Error sending message to client: {e}")

# WebSocket handler function
async def websocket_handler(websocket, path):
    print("New WebSocket connection")
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.recv()  # Keep connection alive
    except websockets.exceptions.ConnectionClosed as e:
        print(f"WebSocket connection closed: {e}")
    finally:
        connected_clients.remove(websocket)

# Function to start the WebSocket server
async def start_websocket_server():
    server = await websockets.serve(websocket_handler, "0.0.0.0", 5005)
    print("WebSocket server started on ws://0.0.0.0:5005")
    await server.wait_closed()

# Function to start everything
async def start():
    # Start RabbitMQ consumer
    await connect_to_queue()

    # Start WebSocket server
    await start_websocket_server()

if __name__ == '__main__':
    asyncio.run(start())
