"""
    This module contains the implementation of various metrics
    For now this is a placeholder for the metrics implementation
    Containing simply the accuracy, precision and recall metrics
    For a binary classification problem
"""

# TODO: Update pydocs for regression tasks

from typing import Callable
from metrics.models import (
    CalculateRequest,
    MetricValues,
)
from metrics.utils import (
    _query_model,
    _lime_explanation,
    _finite_difference_gradient
)
from sklearn.metrics import (
    f1_score,
    roc_auc_score,
    mean_absolute_error as mae,
    mean_squared_error as mse,
    r2_score,
)
from sklearn.metrics.pairwise import cosine_similarity
from aif360.metrics import ClassificationMetric
from aif360.datasets import BinaryLabelDataset
import pandas as pd
import numpy as np
from metrics.exceptions import (
    MetricsComputationException,
    DataInconsistencyException,
    DataProvisionException,
    _MetricsPackageException
)
from common.models import ModelResponse
from metrics.numerical_metrics import (
    accuracy,
    macro_precision,
    macro_recall,
    macro_f1,
    class_precision,
    class_recall,
    class_f1,
    roc_auc,
    mean_absolute_error,
    mean_squared_error,
    r_squared,
    explanation_fidelity_score,
    explanation_sparsity_score,
    explanation_stability_score,
    ood_auroc,
    create_fairness_metric_fn,
    equalized_odds_difference
)

task_type_to_metric = {
    "binary_classification": {
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "roc_auc",
        "statistical_parity_difference",
        "equal_opportunity_difference",
        "equalized_odds_difference",
        "disparate_impact",
        "false_negative_rate_difference",
        "negative_predictive_value",
        "positive_predictive_value",
        "true_positive_rate_difference",
        "explanation_stability_score",
        "explanation_sparsity_score",
        "explanation_fidelity_score",
        "ood_auroc",
    },
    "multi_class_classification": {
        "accuracy",
        "class_precision",
        "precision",
        "class_recall",
        "recall",
        "class_f1_score",
        "f1_score",
        "roc_auc",
        "explanation_stability_score",
        "explanation_sparsity_score",
        "explanation_fidelity_score",
        "ood_auroc",
    },
    "regression": [
        "mean_absolute_error",
        "mean_squared_error",
        "r_squared",
        "explanation_stability_score",
        "explanation_sparsity_score",
        "explanation_fidelity_score",
    ],
}


""" Mapping of metric names to their corresponding functions and required inputs"""
metric_to_fn_and_requirements = {
    # Performance metrics
    "accuracy": {
        "function": accuracy,
        "required_inputs": ["true_labels", "predicted_labels"]
    },
    "class_precision": {
        "function": class_precision,
        "required_inputs": ["true_labels", "predicted_labels", "target_class"]
    },
    "precision": {
        "function": macro_precision,
        "required_inputs": ["true_labels", "predicted_labels"]
    },
    "class_recall": {
        "function": class_recall,
        "required_inputs": ["true_labels", "predicted_labels", "target_class"]
    },
    "recall": {
        "function": macro_recall,
        "required_inputs": ["true_labels", "predicted_labels"]
    },
    "class_f1_score": {
        "function": class_f1,
        "required_inputs": ["true_labels", "predicted_labels"]
    },
    "f1_score": {
        "function": macro_f1,
        "required_inputs": ["true_labels", "predicted_labels"]
    },
    "roc_auc": {
        "function": roc_auc,
        "required_inputs": ["true_labels", "predicted_labels"]
    },
    "mean_absolute_error": {
        "function": mean_absolute_error,
        "required_inputs": ["true_labels", "predicted_labels"]
    },
    "mean_squared_error": {
        "function": mean_squared_error,
        "required_inputs": ["true_labels", "predicted_labels"]
    },
    "r_squared": {
        "function": r_squared,
        "required_inputs": ["true_labels", "predicted_labels"]
    },

    # Fairness metrics
    **{
        metric_name: {
            "function": create_fairness_metric_fn(
                lambda metric, name=metric_name: getattr(metric, name)()
            ),
            "required_inputs": [
                "true_labels",
                "predicted_labels",
                "protected_attr",
                "privileged_groups",
                "unprivileged_groups"
            ]
        }
        for metric_name in [
            "statistical_parity_difference",
            "equal_opportunity_difference",
            "disparate_impact",
            "false_negative_rate_difference",
            "negative_predictive_value",
            "positive_predictive_value",
            "true_positive_rate_difference",
        ]
    },
    "equalized_odds_difference": {
        "function": equalized_odds_difference,
        "required_inputs": ["true_labels", "predicted_labels", "protected_attr"]
    },

    # Explainability metrics
    "explanation_stability_score": {
        "function": explanation_stability_score,
        "required_inputs": ["input_features", "confidence_scores", "model_url", "model_api_key"]
    },
    "explanation_sparsity_score": {
        "function": explanation_sparsity_score,
        "required_inputs": ["input_features", "confidence_scores", "model_url", "model_api_key"]
    },
    "explanation_fidelity_score": {
        "function": explanation_fidelity_score,
        "required_inputs": ["input_features", "confidence_scores", "model_url", "model_api_key"]
    },

    # Uncertainty metrics
    "ood_auroc": {
        "function": ood_auroc,
        "required_inputs": ["input_features", "confidence_scores", "model_url", "model_api_key"]
    },
}


def check_all_required_fields_present(metrics: set[str], info: CalculateRequest):
    """
    check_all_required_fields_present ensures that all the required fields are present in the
    CalculateRequest object.

    :param info: CalculateRequest - contains information required to calculate the metric.

    :return: None
    """
    metrics_to_exceptions = {}
    for metric in metrics:
        if metric not in metric_to_fn_and_requirements:
            metrics_to_exceptions[metric] = MetricsComputationException(
                metric,
                detail="Metric should be supported, but is not mapped to a computation. (Internal Error)"
            )
        else:
            missing_fields = []
            for field in metric_to_fn_and_requirements[metric]["required_inputs"]:
                if not hasattr(info, field) or getattr(info, field) is None:
                    missing_fields.append(field)
            if missing_fields:
                metrics_to_exceptions[metric] = DataProvisionException(
                    detail=f"The following missing fields are required to calculate metric {metric}:\n"
                           f"{missing_fields}"
                )
    return metrics_to_exceptions


def check_metrics_are_supported_for_task(info: CalculateRequest):
    """
    check_metrics_are_supported_for_task ensures that the metrics requested are supported
    for the task type provided.
    """
    if info.task_name not in task_type_to_metric:
        raise DataProvisionException(
            detail=f"Task {info.task_name} is not supported. Please choose a valid task."
        )

    invalid_metrics = set(info.metrics) - task_type_to_metric[info.task_name]
    metrics_to_exceptions = {}
    for metric in invalid_metrics:
        metrics_to_exceptions[metric] = MetricsComputationException(
            metric,
            detail=(
                f"Metric {metric} is not supported for {info.task_name} tasks."
                " Please only choose valid metrics for the task type."
                "\nSupported metrics for this task type are:\n"
                f" {task_type_to_metric[info.task_name]}"
            ),
            status_code=400
        )
    return metrics_to_exceptions


def calculate_metrics(info: CalculateRequest) -> MetricValues:
    """
    calculate_metrics, given a request for calculation of certain metrics and information
    necessary for calculation, attempt to calculate and return the metrics and their scores
    for the given model and dataset.

    :param info: CalculateRequest - contains list of metrics to be calculated and additional
    data required for calculation of these metrics.
    :return: MetricValues - contains the calculated metrics and their scores
    """
    current_metric = "calculate_metrics"

    # Input validation
    if info.confidence_scores is not None:
        if info.predicted_labels is not None:
            # If confidence scores and labels are both given, ensure they have the same length
            if info.confidence_scores.shape[0] != info.predicted_labels.shape[0]:
                raise DataInconsistencyException(
                    detail="Length mismatch between confidence scores and true labels.",
                )

    results = {}

    if info.task_name:
        # Add all metrics to results if they raise an exception
        results = check_metrics_are_supported_for_task(info)
        print(results)
        results = results | check_all_required_fields_present(
            set(info.metrics) - set(results.keys()),
            info
        )
        print(results)

    for metric in info.metrics:
        metric = metric.replace(" ", "_")
        try:
            # Skip the metric if it is known to throw an error
            if metric in results:
                continue
            current_metric = metric
            results[metric] = metric_to_fn_and_requirements[metric]["function"](info)

        # Return an exception in place of the metric result if applicable
        # Approach allows valid metrics to still be calculated
        except _MetricsPackageException as e:
            results[metric] = e
        except Exception as e:
            results[metric] = MetricsComputationException(current_metric, detail=str(e))
    print(results)
    return MetricValues(
        metric_values=results,
        batch_size=info.batch_size,
        total_sample_size=info.total_sample_size
    )
