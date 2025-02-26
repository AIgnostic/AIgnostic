from metrics.metrics import (
    is_valid_for_per_class_metrics,
    accuracy,
    class_precision,
    macro_precision,
    class_recall,
    macro_recall,
    create_fairness_metric_fn,
    _prepare_datasets,
    calculate_metrics,
    class_f1,
    macro_f1,
    roc_auc,
    mean_absolute_error,
    mean_squared_error,
    r_squared,
)
from metrics.exceptions import (
    MetricsComputationException,
    DataInconsistencyException,
    DataProvisionException
)
from metrics.models import CalculateRequest, MetricsPackageExceptionModel
import pytest


@pytest.mark.parametrize(
    "true_labels, predicted_labels, expected",
    [
        (
            [[1], [0], [1], [1], [0], [1], [0], [0]],
            [[1], [0], [1], [0], [0], [1], [1], [0]],
            0.75,
        ),
    ],
)
def test_accuracy(true_labels, predicted_labels, expected):
    info = CalculateRequest(
        batch_size=1,
        total_sample_size=10,
        metrics=["accuracy"],
        true_labels=true_labels,
        predicted_labels=predicted_labels,
    )
    result = accuracy(info)
    assert result == expected


@pytest.mark.parametrize(
    "true_labels, exception_message, expected_exception_type",
    [
        (
            [[2, 3], [0, 3], [2, 3], [2, 3], [0, 3], [2, 3], [0, 3], [0, 3]],
            "Multiple attributes provided",
            MetricsComputationException,
        ),
        ([], "No labels provided", DataProvisionException),
    ],
)
def test_multiple_labels_causes_per_class_metrics_to_error(true_labels, exception_message,
                                                           expected_exception_type):
    with pytest.raises(expected_exception_type) as e:
        is_valid_for_per_class_metrics("class_precision", true_labels)
    assert exception_message in e.value.detail


@pytest.mark.parametrize(
    "metric_fn, metric_name, true_labels, predicted_labels, target_class, expected",
    [
        (
            class_precision,
            "class_precision",
            [[2], [0], [2], [2], [0], [2], [0], [0]],
            [[2], [0], [2], [0], [0], [2], [2], [2]],
            2,
            0.6,
        ),
        (
            macro_precision,
            "precision",
            [[2], [0], [2], [2], [0], [2], [0], [0]],
            [[2], [0], [2], [0], [0], [2], [2], [2]],
            None,
            0.6333333,
        ),
        (
            class_recall,
            "class_recall",
            [[2], [0], [2], [2], [0], [2], [0], [0]],
            [[2], [0], [2], [0], [0], [2], [2], [2]],
            2,
            0.75,
        ),
        (
            macro_recall,
            "recall",
            [[2], [0], [2], [2], [0], [2], [0], [0]],
            [[2], [0], [2], [0], [0], [2], [2], [2]],
            None,
            0.625,
        ),
        (
            class_f1,
            "class_f1",
            [[1], [0], [1], [1], [0], [1], [0], [0]],
            [[1], [0], [1], [0], [0], [1], [1], [0]],
            1,
            0.75,
        ),
        (
            macro_f1,
            "macro_f1",
            [[1], [0], [1], [1], [0], [1], [0], [0]],
            [[1], [0], [1], [0], [0], [1], [1], [0]],
            None,
            0.75,
        ),
        (
            roc_auc,
            "roc_auc",
            [[1], [0], [1], [1], [0], [1], [0], [0]],
            [[1], [0], [1], [0], [0], [1], [1], [0]],
            None,
            0.75,
        ),
        (
            mean_absolute_error,
            "mean_absolute_error",
            [[1.0], [0.0], [1.0], [1.0]],
            [[0.8], [0.1], [0.9], [1.2]],
            None,
            0.15,
        ),
        (
            mean_squared_error,
            "mean_squared_error",
            [[1.0], [0.0], [1.0], [1.0]],
            [[0.8], [0.1], [0.9], [1.2]],
            None,
            0.025,
        ),
        (
            r_squared,
            "r_squared",
            [[3.0], [5.0], [2.5], [7.0]],
            [[2.8], [5.1], [2.6], [6.8]],
            None,
            0.9921182,
        ),
    ],
)
def test_metrics(
    metric_fn, metric_name, true_labels, predicted_labels, target_class, expected
):
    info = CalculateRequest(
        batch_size=1,
        total_sample_size=10,
        metrics=[metric_name],
        true_labels=true_labels,
        predicted_labels=predicted_labels,
        target_class=target_class,
    )
    result = metric_fn(info)
    assert round(result, 7) == round(expected, 7)


@pytest.mark.parametrize(
    "metric_name, expected",
    [
        ("disparate_impact", 0.5),
        ("equal_opportunity_difference", 0.25),
        ("equalized_odds_difference", 0.0),
        ("false_negative_rate_difference", -0.25),
        ("negative_predictive_value", 0.2),
        ("positive_predictive_value", 1 / 3),
        ("statistical_parity_difference", -0.25),
        ("true_positive_rate_difference", 0.25),
    ],
)
def test_fairness_metrics(metric_name, expected):
    info = CalculateRequest(
        batch_size=1,
        total_sample_size=10,
        metrics=[metric_name],
        true_labels=[[1], [0], [1], [1], [0], [1], [0], [1]],
        predicted_labels=[[1], [0], [0], [0], [1], [0], [1], [0]],
        privileged_groups=[{"protected_attr": 1}],
        unprivileged_groups=[{"protected_attr": 0}],
        protected_attr=[0, 1, 0, 0, 1, 0, 1, 1],
    )
    result = create_fairness_metric_fn(lambda metric: getattr(metric, metric_name)())(info)
    assert result == expected


def test_multiple_metrics():
    info = CalculateRequest(
        batch_size=1,
        total_sample_size=10,
        metrics=["accuracy", "class_precision", "class_recall"],
        true_labels=[[2], [0], [2], [2], [0], [2], [0], [0]],
        predicted_labels=[[2], [0], [2], [0], [0], [2], [2], [2]],
        target_class=2,
    )
    results = {
        "accuracy": accuracy(info),
        "class_precision": class_precision(info),
        "class_recall": class_recall(info),
    }
    assert results == {
        "accuracy": 0.625,
        "class_precision": 0.6,
        "class_recall": 0.75,
    }


def test_multiple_binary_classifier_metrics():
    info = CalculateRequest(
        batch_size=1,
        total_sample_size=10,
        metrics=[
            "disparate_impact",
            "equal_opportunity_difference",
            "equalized_odds_difference",
        ],
        true_labels=[[1], [0], [1], [1], [0], [1], [0], [1]],
        predicted_labels=[[1], [0], [0], [0], [1], [0], [1], [0]],
        privileged_groups=[{"protected_attr": 1}],
        unprivileged_groups=[{"protected_attr": 0}],
        protected_attr=[0, 1, 0, 0, 1, 0, 1, 1],
    )
    results = {
        "disparate_impact": create_fairness_metric_fn(
            lambda metric: metric.disparate_impact()
        )(info),
        "equal_opportunity_difference": create_fairness_metric_fn(
            lambda metric: metric.equal_opportunity_difference()
        )(info),
        "equalized_odds_difference": create_fairness_metric_fn(
            lambda metric: metric.equalized_odds_difference()
        )(info),
    }
    expected_metrics = {
        "disparate_impact": 0.5,
        "equal_opportunity_difference": 0.25,
        "equalized_odds_difference": 0.0,
    }
    for metric, value in expected_metrics.items():
        assert round(results[metric], 7) == round(
            value, 7
        ), f"Expected {metric} to be {value}, but got {results.metric_values[metric]}"


def test_zero_division_fairness_metrics_return_0():
    info = CalculateRequest(
        batch_size=1,
        total_sample_size=10,
        metrics=[
            "equal_opportunity_difference",
        ],
        true_labels=[[1], [0], [1], [1], [0], [1], [0], [0]],
        predicted_labels=[[1], [0], [1], [1], [0], [1], [1], [1]],
        privileged_groups=[{"protected_attr": 1}],
        unprivileged_groups=[{"protected_attr": 0}],
        protected_attr=[0, 1, 0, 0, 1, 0, 1, 1],
    )
    results = create_fairness_metric_fn(
        lambda metric: metric.equal_opportunity_difference()
    )(info)
    assert results == 0


def test_error_if_no_protected_attrs():
    info = CalculateRequest(
        batch_size=1,
        total_sample_size=10,
        metrics=["disparate_impact"],
        true_labels=[[1], [0], [1], [1], [0], [1], [0], [1]],
        predicted_labels=[[1], [0], [0], [0], [1], [0], [1], [0]],
        privileged_groups=[{"protected_attr": 1}],
        unprivileged_groups=[{"protected_attr": 0}],
    )
    with pytest.raises(ValueError) as e:
        _prepare_datasets(info)
    assert "protected_attr is missing" in str(e.value)


async def test_calculate_metrics():
    info = CalculateRequest(
        batch_size=1,
        total_sample_size=10,
        metrics=["accuracy", "class_precision", "class_recall"],
        true_labels=[[2], [0], [2], [2], [0], [2], [0], [0]],
        predicted_labels=[[2], [0], [2], [0], [0], [2], [2], [2]],
        target_class=2,
    )
    results = calculate_metrics(info)
    expected_results = {
        "accuracy": 0.625,
        "class_precision": 0.6,
        "class_recall": 0.75,
    }
    for metric, value in expected_results.items():
        computed_value = results.metric_values[metric].computed_value
        assert round(computed_value) == round(
            value, 7
        ), f"Expected {metric} to be {value}, but got {computed_value}"


async def test_calculate_performance_metrics():
    info = CalculateRequest(
        batch_size=1,
        total_sample_size=10,
        metrics=[
            "mean_absolute_error",
            "mean_squared_error",
            "r_squared",
            "roc_auc",
            "class_f1",
            "macro_f1",
        ],
        true_labels=[[1.0], [0.0], [1.0], [1.0], [0.0], [1.0], [0.0], [1.0], [0.0], [1.0]],
        predicted_labels=[[0.9], [0.3], [0.6], [0.7], [0.2], [0.8], [0.1], [0.4], [0.5], [0.35]],
        target_class=1,
    )
    results = calculate_metrics(info)
    expected_results = {
        "mean_absolute_error": 0.335,
        "mean_squared_error": 0.14725,
        "r_squared": 0.3864583,
        "roc_auc": 0.9166667,
        "class_f1": 1.0,
        "macro_f1": 1.0,
    }
    for metric, value in expected_results.items():
        computed_value = results.metric_values[metric].computed_value
        assert round(computed_value, 7) == round(
            value, 7
        ), f"Expected {metric} to be {value}, but got {computed_value}"


def test_calculate_fairness_metrics():
    info = CalculateRequest(
        batch_size=1,
        total_sample_size=10,
        metrics=[
            "statistical_parity_difference",
            "disparate_impact",
            "equal_opportunity_difference",
            "equalized_odds_difference",
            "false_negative_rate_difference",
            "negative_predictive_value",
            "positive_predictive_value",
            "true_positive_rate_difference",
        ],
        true_labels=[[1], [0], [1], [1], [0], [1], [0], [1]],
        predicted_labels=[[1], [1], [0], [1], [0], [0], [1], [1]],
        privileged_groups=[{"protected_attr": 1}],
        unprivileged_groups=[{"protected_attr": 0}],
        protected_attr=[0, 1, 0, 1, 1, 0, 1, 0],
    )
    results = calculate_metrics(info)
    expected_results = {
        "statistical_parity_difference": -0.25,
        "disparate_impact":  0.6666667,
        "equal_opportunity_difference": -0.5,
        "equalized_odds_difference": 0.1666667,
        "false_negative_rate_difference": 0.5,
        "negative_predictive_value": 1 / 3,
        "positive_predictive_value": 0.6,
        "true_positive_rate_difference": -0.5,
    }
    for metric, value in expected_results.items():
        computed_value = results.metric_values[metric].computed_value
        assert round(computed_value, 7) == round(
            value, 7
        ), f"Expected {metric} to be {value}, but got {computed_value}"


def test_calculate_metrics_with_missing_information_returns_insufficient_data_errors():
    info = CalculateRequest(
        metrics=["accuracy"],
        task_name="binary_classification",
        batch_size=1,
        total_sample_size=10,
    )
    results = calculate_metrics(info)
    assert results.metric_values == {
        "accuracy": MetricsPackageExceptionModel(
            detail="Insufficient or invalid data provided to calculate user metrics: "
                   "The following missing fields are required to calculate metric "
                   "accuracy:\n['true_labels', 'predicted_labels']",
            status_code=400,
            exception_type="DataProvisionException",
        )
    }


def test_calculate_metrics_with_invalid_data_throws_data_inconsistency_error():
    info = CalculateRequest(
        batch_size=1,
        total_sample_size=10,
        metrics=["accuracy"],
        true_labels=[[1], [0], [1]],
        predicted_labels=[[1], [0], [1]],
        confidence_scores=[[1]]
    )
    with pytest.raises(DataInconsistencyException) as e:
        calculate_metrics(info)
        assert "Data inconsistency error" in e.value.detail
        assert "Length mismatch between confidence scores and true labels" in e.value.detail
