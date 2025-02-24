import pytest
from unittest.mock import MagicMock, patch
from aggregator.aggregator import (RESULT_QUEUE,
                                   ResultsConsumer,
                                   on_result_fetched,
                                   MetricsAggregator,
                                   aggregator_intermediate_metrics_log,
                                   aggregator_metrics_completion_log,
                                   aggregator_final_report_log,
                                   metrics_aggregator
                                   )
import json


@pytest.fixture
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
    mock_send_to_clients.assert_any_call(aggregator_intermediate_metrics_log(metrics_aggregator.get_aggregated_metrics()))

    # Simulate processing all batches
    on_result_fetched(mock_channel, mock_method, mock_properties, message_body)

    # Verify completion and final report messages were sent
    mock_send_to_clients.assert_any_call(aggregator_metrics_completion_log())
    mock_send_to_clients.assert_any_call(aggregator_final_report_log(mock_report))

    # Ensure metrics are reset after completion
    assert metrics_aggregator.metrics == {}
    assert metrics_aggregator.samples_processed == 0
