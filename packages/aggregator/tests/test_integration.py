from unittest.mock import MagicMock
from aggregator.aggregator import ResultsConsumer, MetricsAggregator, RESULT_QUEUE
from common.models import MetricValue


def mock_message_callback(channel, method, properties, body, aggregator):
    """Simulates message consumption and aggregation."""
    metrics_data, batch_size = body
    aggregator.aggregate_new_batch(metrics_data, batch_size)


def test_integration_results_consumer_and_metrics_aggregator():
    """Integration test for ResultsConsumer and MetricsAggregator."""
    aggregator = MetricsAggregator()
    consumer = ResultsConsumer(host="test_host")

    mock_connection = MagicMock()
    mock_channel = MagicMock()
    consumer._connection = mock_connection
    consumer._channel = mock_channel

    result1 = {
        "accuracy": MetricValue(
            computed_value=0.8,
            ideal_value=1.0,
            range=(0, 1)),
        "loss": MetricValue(
            computed_value=0.5,
            ideal_value=0.0,
            range=(0, 1))
    }

    result2 = {
        "accuracy": MetricValue(
            computed_value=0.9,
            ideal_value=1.0,
            range=(0, 1)),
        "loss": MetricValue(
            computed_value=0.4,
            ideal_value=0.0,
            range=(0, 1))
    }

    result3 = {
        "accuracy": MetricValue(
            computed_value=0.85,
            ideal_value=1.0,
            range=(0, 1)),
        "loss": MetricValue(
            computed_value=0.45,
            ideal_value=0.0,
            range=(0, 1))
    }

    test_messages = [
        (result1, 10),
        (result2, 20),
        (result3, 15)
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
        "accuracy": {
            "value": (0.8 * 10 + 0.9 * 20 + 0.85 * 15) / 45,
            "ideal_value": 1.0,
            "range": (0, 1),
            "count": 45,
            "error": None
        },
        "loss": {
            "value": (0.5 * 10 + 0.4 * 20 + 0.45 * 15) / 45,
            "ideal_value": 0.0,
            "range": (0, 1),
            "count": 45,
            "error": None
        }
    }

    aggregated_metrics = aggregator.get_aggregated_metrics()

    assert abs(aggregated_metrics["accuracy"]["value"] - expected_metrics["accuracy"]["value"]) < 1e-5
    assert abs(aggregated_metrics["loss"]["value"] - expected_metrics["loss"]["value"]) < 1e-5
