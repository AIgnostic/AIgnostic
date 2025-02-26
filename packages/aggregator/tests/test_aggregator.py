import time
import pytest
from unittest.mock import MagicMock, patch
from aggregator.aggregator import (RESULT_QUEUE, MetricsAggregator,
                                   ResultsConsumer, aggregator_generate_report,
                                   on_result_fetched,
                                   aggregator_intermediate_metrics_log,
                                   aggregator_metrics_completion_log,
                                   aggregator_final_report_log,
                                   connected_clients,
                                   message_queue,
                                   websocket_handler,
                                   send_to_clients,
                                   user_aggregators,
                                   manager,
                                   )
import json


@pytest.fixture(scope="module")
def consumer():
    return ResultsConsumer(host="test_host")

metrics_aggregator = MetricsAggregator()

@pytest.fixture(autouse=True)
def reset_state():
    metrics_aggregator.metrics = {}
    metrics_aggregator.samples_processed = 0
    metrics_aggregator.total_sample_size = 0
    user_aggregators.clear()
    connected_clients.clear()
    while not message_queue.empty():
        message_queue.get()

def test_init(consumer):
    assert consumer._host == "test_host"
    assert consumer._connection is None
    assert consumer._channel is None


@patch('aggregator.aggregator.connect_to_rabbitmq')
@patch('aggregator.aggregator.init_queues')
def test_connect(mock_init_queues, mock_connect_to_rabbitmq, consumer):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_connect_to_rabbitmq.return_value = mock_connection
    mock_connection.channel.return_value = mock_channel

    consumer.connect()

    mock_connect_to_rabbitmq.assert_called_once_with(host="test_host")
    mock_connection.channel.assert_called_once()
    mock_init_queues.assert_called_once_with(mock_channel)
    assert consumer._connection == mock_connection
    assert consumer._channel == mock_channel

    # Add these print statements for debugging
    print(f"mock_connect_to_rabbitmq called: {mock_connect_to_rabbitmq.called}")
    print(f"mock_init_queues called: {mock_init_queues.called}")


@patch('aggregator.aggregator.init_queues')
@patch('aggregator.aggregator.connect_to_rabbitmq')
def test_run(mock_init_queues, mock_connect_to_rabbitmq, consumer):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_connect_to_rabbitmq.return_value = mock_connection
    mock_connection.channel.return_value = mock_channel

    consumer.connect = MagicMock()
    consumer._connection = mock_connection
    consumer._channel = mock_channel

    mock_callback = MagicMock()
    mock_channel.start_consuming = MagicMock()

    consumer.run(on_message_callback=mock_callback)

    mock_channel.basic_consume.assert_called_once_with(
        queue=RESULT_QUEUE,
        on_message_callback=mock_callback,
        auto_ack=True
    )
    mock_channel.start_consuming.assert_called_once()


@patch('aggregator.aggregator.connect_to_rabbitmq')
@patch('aggregator.aggregator.init_queues')
def test_stop(mock_init_queues, mock_connect_to_rabbitmq, consumer):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    consumer._connection = mock_connection
    consumer._channel = mock_channel

    consumer.stop()

    mock_channel.close.assert_called_once()
    mock_connection.close.assert_called_once()


@patch('aggregator.aggregator.connect_to_rabbitmq')
@patch('aggregator.aggregator.init_queues')
@patch.object(ResultsConsumer, 'stop')  # Mock stop to prevent real shutdown
def test_run_keyboard_interrupt(mock_stop, mock_init_queues, mock_connect_to_rabbitmq, consumer):
    mock_connection = MagicMock()
    mock_channel = MagicMock()

    mock_connect_to_rabbitmq.return_value = mock_connection
    mock_connection.channel.return_value = mock_channel

    consumer.connect = MagicMock()  # Prevent real connection logic
    consumer._connection = mock_connection
    consumer._channel = mock_channel

    mock_callback = MagicMock()

    # Simulate `start_consuming` raising a KeyboardInterrupt
    mock_channel.start_consuming.side_effect = KeyboardInterrupt

    consumer.run(on_message_callback=mock_callback)

    # Ensure that stop() is called when KeyboardInterrupt occurs
    mock_stop.assert_called_once()


@patch('aggregator.aggregator.manager.send_to_user')
@patch('aggregator.aggregator.generate_report')
def test_on_result_fetched(mock_generate_report, mock_send_to_user):
    # Create dummy RabbitMQ parameters (not used in logic).
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_properties = MagicMock()

    # Define sample incoming message with a user_id.
    sample_message = {
        "user_id": "user123",
        "total_sample_size": 20,
        "batch_size": 10,
        "metric_values": {"accuracy": 0.85, "precision": 0.15}
    }
    message_body = json.dumps(sample_message)

    # Set the expected report that generate_report should return.
    mock_report = {"summary": "Test Report"}
    mock_generate_report.return_value = mock_report

    # Call on_result_fetched for the first batch.
    on_result_fetched(mock_channel, mock_method, mock_properties, message_body)

    # After first call, a per-user aggregator should be created.
    aggregator = user_aggregators.get("user123")
    assert aggregator is not None, "Aggregator for user123 should be initialized."
    assert aggregator.total_sample_size == 20, "Total sample size should be set to 20."
    assert aggregator.samples_processed == 10, "Samples processed should be 10 after first batch."
    intermediate_metrics = aggregator.get_aggregated_metrics()

    # Verify that an intermediate metrics message was sent.
    mock_send_to_user.assert_any_call("user123", aggregator_intermediate_metrics_log(intermediate_metrics))

    # Simulate processing the second (final) batch.
    on_result_fetched(mock_channel, mock_method, mock_properties, message_body)

    # Allow the reporting thread a moment to start.
    time.sleep(0.1)

    # Verify that completion and final report messages were sent.
    calls = mock_send_to_user.call_args_list
    completion_called = any(call[0][1] == aggregator_metrics_completion_log() for call in calls)
    # final_called = any(call[0][1] == aggregator_final_report_log(mock_report) for call in calls)
    assert completion_called, "Completion log was not sent."
    # assert final_called, "Final report log was not sent."

    # Ensure the per-user aggregator is cleaned up after completion.
    assert "user123" not in user_aggregators, "Aggregator for user123 should be removed after processing."
    
@patch('aggregator.aggregator.manager.send_to_user')
def test_websocket_handler(mock_send_to_user):
    # Create a dummy websocket that returns a user_id and supports iteration.
    class DummyWebsocket:
        def __init__(self, user_id):
            self.user_id = user_id
            self.sent_messages = []
            self.iterated = False

        def recv(self):
            return self.user_id

        def send(self, message):
            self.sent_messages.append(message)

        def __iter__(self):
            if not self.iterated:
                self.iterated = True
                yield "dummy"
            else:
                return iter([])

    user_id = "user456"
    dummy_ws = DummyWebsocket(user_id)

    # Call the websocket handler.
    websocket_handler(dummy_ws)

    # After the handler finishes, the user should be disconnected.
    assert user_id not in manager.active_connections


def test_send_to_clients_no_clients():
    # Mock message
    mock_message = "Test Message"
    mesg = aggregator_intermediate_metrics_log(mock_message)

    # Reset connected clients
    connected_clients.clear()

    # Call function under test
    send_to_clients(mesg)

    # Ensure message is stored in the queue
    assert message_queue.qsize() == 1


def test_send_to_clients_with_clients():
    # Mock WebSocket clients
    mock_client1 = MagicMock()
    mock_client2 = MagicMock()
    connected_clients.clear()
    connected_clients.add(mock_client1)
    connected_clients.add(mock_client2)

    # Mock message
    mock_message = "Test Message"
    mesg = aggregator_intermediate_metrics_log(mock_message)

    # Call function under test
    send_to_clients(mesg)

    # Ensure message is sent to all clients
    mock_client1.send.assert_called_once()
    mock_client2.send.assert_called_once()


@patch('aggregator.aggregator.generate_report')
def test_aggregate_report(mock_generate_report):
    # Mock metrics data
    metrics = {
        "accuracy": 0.85,
        "precision": 0.15
    }

    # Mock report generation functions
    mock_generate_report.return_value = []
    with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_value'}):
        # Call function under test
        report = aggregator_generate_report(metrics, metrics_aggregator)

        # Ensure report is generated correctly
        assert "properties" in report
        assert "info" in report
        mock_generate_report.assert_called_once_with(metrics, "test_value")
