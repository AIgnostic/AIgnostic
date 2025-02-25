import pytest
from unittest.mock import MagicMock, patch
from aggregator.aggregator import (RESULT_QUEUE,
                                   ResultsConsumer,
                                   on_result_fetched,
                                   aggregator_intermediate_metrics_log,
                                   aggregator_metrics_completion_log,
                                   aggregator_final_report_log,
                                   metrics_aggregator,
                                   connected_clients,
                                   message_queue,
                                   websocket_handler,
                                   send_to_clients,
                                   aggregate_report
                                   )
import json


@pytest.fixture(scope="module")
def consumer():
    return ResultsConsumer(host="test_host")


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


@patch('aggregator.aggregator.send_to_clients')  # Mock send_to_clients
@patch('aggregator.aggregator.aggregate_report')  # Mock report generation
def test_on_result_fetched(mock_aggregate_report, mock_send_to_clients):
    # Mock RabbitMQ parameters
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_properties = MagicMock()

    # Define sample incoming message
    sample_message = {
        "total_sample_size": 20,
        "batch_size": 10,
        "metric_values": {"accuracy": 0.85, "precision": 0.15}
    }
    message_body = json.dumps(sample_message)

    # Reset aggregator state before test
    metrics_aggregator.metrics = {}
    metrics_aggregator.samples_processed = 0
    metrics_aggregator.total_sample_size = 0  # Ensures total size is set

    # Mock the report generation function return value
    mock_report = {"summary": "Test Report"}
    mock_aggregate_report.return_value = mock_report

    # Call function under test
    on_result_fetched(mock_channel, mock_method, mock_properties, message_body)

    # Check if total sample size is set correctly
    assert metrics_aggregator.total_sample_size == 20

    # Check if batch was aggregated
    assert "accuracy" in metrics_aggregator.metrics
    assert "precision" in metrics_aggregator.metrics
    assert metrics_aggregator.samples_processed == 10

    # Verify send_to_clients was called with intermediate results
    mock_send_to_clients.assert_any_call(
        aggregator_intermediate_metrics_log(metrics_aggregator.get_aggregated_metrics()))

    # Simulate processing all batches
    on_result_fetched(mock_channel, mock_method, mock_properties, message_body)

    # Verify completion and final report messages were sent
    mock_send_to_clients.assert_any_call(aggregator_metrics_completion_log())
    mock_send_to_clients.assert_any_call(aggregator_final_report_log(mock_report))

    # Ensure metrics are reset after completion
    assert metrics_aggregator.metrics == {}
    assert metrics_aggregator.samples_processed == 0


@patch('aggregator.aggregator.send_to_clients')  # Mock send_to_clients
def test_websocket_handler(mock_send_to_clients):
    # Mock WebSocket clients
    mock_client1 = MagicMock()
    connected_clients.clear()

    # Mock message
    mock_message = "Test Message"

    assert not connected_clients
    assert not message_queue.queue
    mesg = aggregator_intermediate_metrics_log(mock_message)
    message_queue.put(mesg)
    assert message_queue.qsize() == 1

    # Call function under test
    # Add clients to connected clients
    websocket_handler(mock_client1)
    # assert len(connected_clients) == 1
    mock_send_to_clients.assert_called_once_with(mesg)


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
        report = aggregate_report(metrics)

        # Ensure report is generated correctly
        assert "properties" in report
        assert "info" in report
        mock_generate_report.assert_called_once_with(metrics, "test_value")
