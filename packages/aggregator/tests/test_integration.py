from unittest.mock import MagicMock
from aggregator.aggregator import ResultsConsumer, MetricsAggregator, RESULT_QUEUE


def mock_message_callback(channel, method, properties, body, aggregator):
    """Simulates message consumption and aggregation."""
    metrics_data, batch_size = eval(body.decode())  # Simulate deserialization
    aggregator.aggregate_new_batch(metrics_data, batch_size)


def test_integration_results_consumer_and_metrics_aggregator():
    """Integration test for ResultsConsumer and MetricsAggregator."""
    aggregator = MetricsAggregator()
    consumer = ResultsConsumer(host="test_host")

    mock_connection = MagicMock()
    mock_channel = MagicMock()
    consumer._connection = mock_connection
    consumer._channel = mock_channel

    # Simulating messages received in the queue
    test_messages = [
        (b"{'accuracy': 0.8, 'loss': 0.5}, 10"),
        (b"{'accuracy': 0.9, 'loss': 0.4}, 20"),
        (b"{'accuracy': 0.85, 'loss': 0.45}, 15")
    ]

    # Mock RabbitMQ's basic_consume and simulate message consumption
    def mock_basic_consume(queue, on_message_callback, auto_ack):
        for message in test_messages:
            mock_message_callback(None, None, None, message, aggregator)

    mock_channel.basic_consume.side_effect = mock_basic_consume

    # Run only the message processing without calling start_consuming
    consumer._channel.basic_consume(RESULT_QUEUE,
                                    lambda ch, method, properties, body:
                                    mock_message_callback(ch, method, properties, body, aggregator),
                                    auto_ack=True)

    # Verify the aggregator received the correct aggregated results
    expected_metrics = {
        "accuracy": (0.8 * 10 + 0.9 * 20 + 0.85 * 15) / 45,
        "loss": (0.5 * 10 + 0.4 * 20 + 0.45 * 15) / 45
    }

    aggregated_metrics = aggregator.get_aggregated_metrics()

    assert abs(aggregated_metrics["accuracy"] - expected_metrics["accuracy"]) < 1e-5
    assert abs(aggregated_metrics["loss"] - expected_metrics["loss"]) < 1e-5
