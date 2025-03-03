from aggregator.aggregator import MetricsAggregator
from common.models import MetricValue, MetricsPackageExceptionModel


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
        "accuracy": MetricValue(
            computed_value=0.8,
            ideal_value=1.0,
            range=(0, 1)),
        "loss": MetricValue(
            computed_value=0.5,
            ideal_value=0.0,
            range=(0, 1))
    }
    aggregator.aggregate_new_batch(metric_info, 10)

    expected_metrics = {
        "accuracy": {
            "value": 0.8,
            "ideal_value": 1.0,
            "range": (0, 1),
            "count": 10,
            "error": None
        },
        "loss": {
            "value": 0.5,
            "ideal_value": 0.0,
            "range": (0, 1),
            "count": 10,
            "error": None
        }
    }
    assert aggregator.metrics == expected_metrics
    assert aggregator.samples_processed == 10


def test_handles_error_in_batch():
    """Test that the aggregator handles errors in the batch."""
    aggregator = MetricsAggregator()
    metric_info = {
        "accuracy": MetricValue(
            computed_value=0.8,
            ideal_value=1.0,
            range=(0, 1)),
        "loss": MetricValue(
            computed_value=0.5,
            ideal_value=0.0,
            range=(0, 1)),
        "error": MetricsPackageExceptionModel(
            detail="An error occurred",
            status_code=500)
    }
    aggregator.aggregate_new_batch(metric_info, 10)

    expected_metrics = {
        "accuracy": {
            "value": 0.8,
            "ideal_value": 1.0,
            "range": (0, 1),
            "count": 10,
            "error": None
        },
        "loss": {
            "value": 0.5,
            "ideal_value": 0.0,
            "range": (0, 1),
            "count": 10,
            "error": None
        },
        "error": {
            "value": None,
            "ideal_value": None,
            "range": None,
            "count": 10,
            "error": "An error occurred"
        }
    }
    assert aggregator.metrics == expected_metrics
    assert aggregator.samples_processed == 10


def test_error_previous_batch_stays_error_in_new_batch():
    """Test that the aggregator retains the error from the previous batch."""
    aggregator = MetricsAggregator()
    metric_info = {
        "accuracy": MetricValue(
            computed_value=0.8,
            ideal_value=1.0,
            range=(0, 1)),
        "loss": MetricValue(
            computed_value=0.5,
            ideal_value=0.0,
            range=(0, 1)),
        "error": MetricsPackageExceptionModel(
            detail="An error occurred",
            status_code=500)
    }
    aggregator.aggregate_new_batch(metric_info, 10)

    metric_info = {
        "accuracy": MetricValue(
            computed_value=0.9,
            ideal_value=1.0,
            range=(0, 1)),
        "loss": MetricValue(
            computed_value=0.4,
            ideal_value=0.0,
            range=(0, 1)),
        "error": MetricValue(
            computed_value=0.6,
            ideal_value=0.0,
            range=(0, None))
    }
    aggregator.aggregate_new_batch(metric_info, 20)

    expected_metrics = {
        "accuracy": {
            "value": (0.8 * 10 + 0.9 * 20) / 30,
            "count": 30,
            "ideal_value": 1.0,
            "range": (0, 1),
            "error": None
        },
        "loss": {
            "value": (0.5 * 10 + 0.4 * 20) / 30,
            "count": 30,
            "ideal_value": 0.0,
            "range": (0, 1),
            "error": None
        },
        "error": {
            "value": None,
            "ideal_value": None,
            "range": None,
            "count": 30,
            "error": "An error occurred"  # stays error from previous batch
        }
    }
    assert aggregator.metrics == expected_metrics
    assert aggregator.samples_processed == 30


def test_aggregate_multiple_batches():
    """Test aggregation with multiple batches."""
    aggregator = MetricsAggregator()
    metric_info1 = {
        "accuracy": MetricValue(
            computed_value=0.8,
            ideal_value=1.0,
            range=(0, 1)),
        "loss": MetricValue(
            computed_value=0.5,
            ideal_value=0.0,
            range=(0, 1))
    }
    aggregator.aggregate_new_batch(metric_info1, 10)

    metric_info2 = {
        "accuracy": MetricValue(
            computed_value=0.9,
            ideal_value=1.0,
            range=(0, 1)),
        "loss": MetricValue(
            computed_value=0.4,
            ideal_value=0.0,
            range=(0, 1))
    }

    aggregator.aggregate_new_batch(metric_info2, 20)

    expected_metrics = {
        "accuracy": {
            "value": (0.8 * 10 + 0.9 * 20) / 30,
            "count": 30,
            "ideal_value": 1.0,
            "range": (0, 1),
            "error": None
        },
        "loss": {
            "value": (0.5 * 10 + 0.4 * 20) / 30,
            "count": 30,
            "ideal_value": 0.0,
            "range": (0, 1),
            "error": None
        }
    }

    assert abs(aggregator.metrics["accuracy"]["value"] - expected_metrics["accuracy"]["value"]) < 1e-5
    assert abs(aggregator.metrics["loss"]["value"] - expected_metrics["loss"]["value"]) < 1e-5
    assert aggregator.samples_processed == 30
