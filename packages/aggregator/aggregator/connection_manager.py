import json
from common.models import AggregatorMessage


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

    def send_to_user(self, user_id, message: AggregatorMessage):
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
