from aggregator.aggregator import MetricsAggregator


def test_initial_state():
    """Test that the initial state of MetricsAggregator is correct."""
    aggregator = MetricsAggregator()
    assert aggregator.metrics == {}
    assert aggregator.samples_processed == 0
    assert aggregator.total_sample_size == 0


def test_set_total_sample_size():
    """Test setting the total sample size."""
    aggregator = MetricsAggregator()
    aggregator.set_total_sample_size(100)
    assert aggregator.total_sample_size == 100


def test_aggregate_new_batch_single_batch():
    """Test aggregation with a single batch."""
    aggregator = MetricsAggregator()
    metric_info = {
        "accuracy": {
            "computed_value": 0.8,
            "ideal_value": 1.0,
            "range": (0, 1)
        },
        "loss": {
            "computed_value": 0.5,
            "ideal_value": 0.0,
            "range": (0, 1)
        }
    }
    aggregator.aggregate_new_batch(metric_info, 10)

    expected_metrics = {
        "accuracy": {
            "value": 0.8,
            "ideal_value": 1.0,
            "range": (0, 1),
            "count": 10
        },
        "loss": {
            "value": 0.5,
            "ideal_value": 0.0,
            "range": (0, 1),
            "count": 10
        }
    }
    assert aggregator.metrics == expected_metrics
    assert aggregator.samples_processed == 10


def test_aggregate_multiple_batches():
    """Test aggregation with multiple batches."""
    aggregator = MetricsAggregator()
    metric_info1 = {
        "accuracy": {
            "computed_value": 0.8,
            "ideal_value": 1.0,
            "range": (0, 1)
        },
        "loss": {
            "computed_value": 0.5,
            "ideal_value": 0.0,
            "range": (0, 1)
        }
    }
    aggregator.aggregate_new_batch(metric_info1, 10)
    metric_info2 = {
        "accuracy": {
            "computed_value": 0.9,
            "ideal_value": 1.0,
            "range": (0, 1)
        },
        "loss": {
            "computed_value": 0.4,
            "ideal_value": 0.0,
            "range": (0, 1)
        }
    }
    aggregator.aggregate_new_batch(metric_info2, 20)

    expected_metrics = {
        "accuracy": {"value": (0.8 * 10 + 0.9 * 20) / 30, "count": 30},
        "loss": {"value": (0.5 * 10 + 0.4 * 20) / 30, "count": 30}
    }

    assert abs(aggregator.metrics["accuracy"]["value"] - expected_metrics["accuracy"]["value"]) < 1e-5
    assert abs(aggregator.metrics["loss"]["value"] - expected_metrics["loss"]["value"]) < 1e-5
    assert aggregator.samples_processed == 30


def test_get_aggregated_metrics():
    """Test retrieving the aggregated metrics."""
    aggregator = MetricsAggregator()
    metric_info1 = {
        "accuracy": {
            "computed_value": 0.8,
            "ideal_value": 1.0,
            "range": (0, 1)
        },
        "loss": {
            "computed_value": 0.5,
            "ideal_value": 0.0,
            "range": (0, 1)
        }
    }
    aggregator.aggregate_new_batch(metric_info1, 10)
    metric_info2 = {
        "accuracy": {
            "computed_value": 0.9,
            "ideal_value": 1.0,
            "range": (0, 1)
        },
        "loss": {
            "computed_value": 0.4,
            "ideal_value": 0.0,
            "range": (0, 1)
        }
    }
    aggregator.aggregate_new_batch(metric_info2, 20)

    aggregated_metrics = aggregator.get_aggregated_metrics()

    expected_metrics = {
        "accuracy": (0.8 * 10 + 0.9 * 20) / 30,
        "loss": (0.5 * 10 + 0.4 * 20) / 30
    }

    assert abs(aggregated_metrics["accuracy"]["value"] - expected_metrics["accuracy"]) < 1e-5
    assert abs(aggregated_metrics["loss"]["value"] - expected_metrics["loss"]) < 1e-5
