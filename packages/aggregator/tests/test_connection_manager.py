import unittest
from unittest.mock import Mock, patch
from aggregator.connection_manager import ConnectionManager
from common.models import AggregatorMessage, MessageType


class TestConnectionManager(unittest.TestCase):
    def setUp(self):
        self.manager = ConnectionManager()
        self.user_id = "user1"
        self.websocket = Mock()

    def test_connect(self):
        self.manager.connect(self.user_id, self.websocket)
        self.assertIn(self.user_id, self.manager.active_connections)
        self.assertEqual(self.manager.active_connections[self.user_id], self.websocket)

    def test_disconnect(self):
        self.manager.connect(self.user_id, self.websocket)
        self.manager.disconnect(self.user_id)
        self.assertNotIn(self.user_id, self.manager.active_connections)

    @patch('aggregator.connection_manager.json.dumps')
    def test_send_to_user_success(self, mock_json_dumps):
        self.manager.connect(self.user_id, self.websocket)
        message = AggregatorMessage(
            messageType=MessageType.LOG,
            message="test message",
            statusCode=200,
            content=None,
        )
        mock_json_dumps.return_value = '{"content": "test message"}'

        self.manager.send_to_user(self.user_id, message)
        self.websocket.send.assert_called_once_with('{"content": "test message"}')

    @patch('aggregator.connection_manager.json.dumps')
    def test_send_to_user_failure(self, mock_json_dumps):
        self.manager.connect(self.user_id, self.websocket)
        message = AggregatorMessage(
            messageType=MessageType.LOG,
            message="test message",
            statusCode=200,
            content=None,
        )
        mock_json_dumps.return_value = '{"content": "test message"}'
        self.websocket.send.side_effect = Exception("send error")

        self.manager.send_to_user(self.user_id, message)
        self.websocket.send.assert_called_once_with('{"content": "test message"}')
        self.assertNotIn(self.user_id, self.manager.active_connections)

    def test_send_to_user_not_connected(self):
        message = AggregatorMessage(
            messageType=MessageType.LOG,
            message="test message",
            statusCode=200,
            content=None,
        )
        with patch('builtins.print') as mock_print:
            self.manager.send_to_user(self.user_id, message)
            mock_print.assert_any_call(f"User not connected: {self.user_id}")
            mock_print.assert_any_call(f"Active connections {self.manager.active_connections}")


if __name__ == '__main__':
    unittest.main()
