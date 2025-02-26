from metrics.models import CalculateRequest, MetricsPackageExceptionModel
from metrics.metrics import calculate_metrics, check_metrics_are_supported_for_task
from metrics.exceptions import DataProvisionException
import pytest
from metrics.metrics import task_type_to_metric


def test_empty_true_labels_returns_metric_exception_for_per_class_metrics():
    """
    Test that DataProvisionExceptions are raised when the true_labels are not provided
    per-class metrics.
    """
    # Arrange
    info = CalculateRequest(
        metrics=["precision", "recall", "f1_score"],
        true_labels=[[], []],
        predicted_labels=[[], []],
        batch_size=2,
        total_sample_size=10
    )
    results = calculate_metrics(info)
    assert results.metric_values
    assert (
        isinstance(results.metric_values["precision"], MetricsPackageExceptionModel)
        and isinstance(results.metric_values["recall"], MetricsPackageExceptionModel)
        and isinstance(results.metric_values["f1_score"], MetricsPackageExceptionModel)
    )
    assert results.metric_values["precision"].detail.endswith(
        "No attributes provided - cannot calculate macro_precision"
    )
    assert results.metric_values["recall"].detail.endswith(
        "No attributes provided - cannot calculate macro_recall"
    )
    assert results.metric_values["f1_score"].detail.endswith(
        "No attributes provided - cannot calculate macro_f1"
    )
    assert results.metric_values["precision"].status_code == 400
    assert results.metric_values["recall"].status_code == 400
    assert results.metric_values["f1_score"].status_code == 400
    assert results.metric_values["precision"].exception_type == "DataProvisionException"
    assert results.metric_values["recall"].exception_type == "DataProvisionException"
    assert results.metric_values["f1_score"].exception_type == "DataProvisionException"


def test_unknown_task_name_raises_data_prov_error():
    """
    Test that a DataProvisionException is raised when an unknown task name is provided.
    """
    # Arrange
    info = CalculateRequest(
        metrics=["accuracy"],
        true_labels=[[1], [0]] * 4,
        predicted_labels=[[1]] * 8,
        task_name="invalid_task_name",
        batch_size=2,
        total_sample_size=10
    )
    with pytest.raises(DataProvisionException) as exc_info:
        check_metrics_are_supported_for_task(info)
        assert exc_info.value.detail == (
            "Data inconsistency error: Task invalid_task_name is not supported. "
            "Please choose a valid task."
        )
        assert exc_info.value.status_code == 400


def test_task_incompatible_metric_returns_error():
    """
    Test that a DataProvisionException is raised when an incompatible metric is requested for a
    given task.
    """
    # Arrange
    info = CalculateRequest(
        metrics=["mean_squared_error"],
        true_labels=[[1], [0]] * 4,
        predicted_labels=[[1]] * 8,
        task_name="binary_classification",
        batch_size=2,
        total_sample_size=10
    )
    results = calculate_metrics(info)
    mse = results.metric_values["mean_squared_error"]
    assert mse  # Check that the metric exists in the dictionary
    assert isinstance(mse, MetricsPackageExceptionModel)
    assert mse.detail.startswith(
        "Error during metric calculation (mean_squared_error): "
        "Metric mean_squared_error is not supported for binary_classification tasks."
        " Please only choose valid metrics for the task type.\nSupported metrics "
        "for this task type are:\n"
    )
    assert mse.status_code == 400
    assert mse.exception_type == "MetricsComputationException"


def test_some_failing_metrics_dont_break_pipeline_for_invalid_input_format():
    """
    Test that when some metrics fail, the pipeline continues to calculate the other metrics.
    """
    task_type_to_metric["binary_classification"].append("explanation_stability_score")
    # Arrange
    info = CalculateRequest(
        metrics=[
            "accuracy",
            "explanation_stability_score",
            "mean_squared_error",
        ],
        true_labels=[[1], [0]] * 4,
        predicted_labels=[[1]] * 8,
        task_name="binary_classification",
        batch_size=2,
        total_sample_size=10
    )
    results = calculate_metrics(info)
    assert results.metric_values
    assert "accuracy" in results.metric_values
    assert isinstance(
        results.metric_values["accuracy"].computed_value,
        float
    )
    assert isinstance(
        results.metric_values["explanation_stability_score"],
        MetricsPackageExceptionModel
    )
    assert isinstance(
        results.metric_values["mean_squared_error"],
        MetricsPackageExceptionModel
    )

    assert results.metric_values["accuracy"].computed_value == 0.5
    assert (
        "The following missing fields are required to calculate metric"
        in results.metric_values["explanation_stability_score"].detail
    )
    assert (
        "Metric mean_squared_error is not supported for binary_classification tasks"
        in results.metric_values["mean_squared_error"].detail
    )
    assert results.metric_values["explanation_stability_score"].status_code == 400
    assert results.metric_values["mean_squared_error"].status_code == 400
    assert results.metric_values["explanation_stability_score"].exception_type == "DataProvisionException"
    assert results.metric_values["mean_squared_error"].exception_type == "MetricsComputationException"
