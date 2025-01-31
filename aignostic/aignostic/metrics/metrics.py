from aignostic.pydantic_models.metric_models import CalculateRequest, MetricsInfo, MetricValues

"""
    This module contains the implementation of various metrics
    For now this is a placeholder for the metrics implementation
    Containing simply the accuracy, precision and recall metrics
    For a binary classification problem
"""

import numpy as np
from fastapi import FastAPI, HTTPException

metrics_app = FastAPI()

task_to_metric_map = {
    "binary_classification": [],
    "multi_class_classification": [],
    "regression": []
}


@metrics_app.get("/retrieve-metric-info", response_model=MetricsInfo)
async def retrieve_info() -> MetricsInfo:
    """
    Retrieve information about the types of tasks expected / supported by the library
    as well as all the metrics that can be calculated for each task type.

    :return: MetricsInfo - contains the mapping from task type to metrics
    """
    return MetricsInfo(task_to_metric_map=task_to_metric_map)


@metrics_app.post("/calculate-metrics", response_model=MetricValues)
async def calculate_metrics(info: CalculateRequest) -> MetricValues:
    """
    calculate_metrics, given a request for calculation of certain metrics and information
    necessary for calculation, attempt to calculate and return the metrics and their scores
    for the given model and dataset.

    :param info: CalculateRequest - contains list of metrics to be calculated and additional
    data required for calculation of these metrics.
    :return: MetricValues - contains the calculated metrics and their scores
    """
    results = {}
    for metric in info.metrics:
        results[metric] = metric_to_fn[metric](metric, info)
    return MetricValues(metric_values=results)


class MetricsException(HTTPException):
    def __init__(self, name, additional_context=None):
        detail = f"Error during metric calculation: {name}"
        if additional_context:
            detail += f"; {additional_context}"
        super().__init__(
            status_code=500,
            detail=detail
        )


def is_valid_for_per_class_metrics(metric_name, true_labels):
    """
    Check if the input is valid for the given metric. Valid fn for precision, recall and F1 scoring
    """
    if len(true_labels) == 0:
        raise MetricsException(
            metric_name,
            additional_context="No labels provided - will lead to division by zero"
        )
    elif len(true_labels[0]) > 1:
        raise MetricsException(
            metric_name,
            additional_context="Multiple attributes provided - cannot calculate precision"
        )
    elif len(true_labels[0]) == 0:
        raise MetricsException(
            metric_name,
            additional_context="No attributes provided - cannot calculate precision"
        )


def accuracy(name, info: CalculateRequest) -> float:
    """
    Calculate the accuracy of the model
    """
    try:
        return (info.true_labels == info.predicted_labels).mean()
    except Exception as e:
        # Catch exceptions generally for now rather than specific ones
        raise MetricsException(name, additional_context=str(e))


def _calculate_precision(metric_name, true_labels, predicted_labels, target_class):
    try:
        target_reshaped = np.full_like(true_labels, target_class)
        tp = np.count_nonzero((true_labels == target_reshaped) & (predicted_labels == target_reshaped))
        fp = np.count_nonzero((true_labels != target_reshaped) & (predicted_labels == target_reshaped))
        return tp / (tp + fp)
    except Exception as e:
        raise MetricsException(metric_name, additional_context=str(e))


def class_precision(name, info: CalculateRequest) -> float:
    """
    Calculate the precision for a given class. The labels/predictions provided must only be for
    one attribute of the predictions. Calculating precisions for multiple attributes will raise
    an exception
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return _calculate_precision(name, info.true_labels, info.predicted_labels, info.target_class)


def macro_precision(name, info: CalculateRequest) -> float:
    """
    Calculate the macro precision for all classes
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return sum(
            [
                _calculate_precision(name, info.true_labels, info.predicted_labels, c)
                for c in np.unique(info.true_labels)
            ]
        ) / len(np.unique(info.true_labels))


def _calculate_recall(metric_name, true_labels, predicted_labels, target_class):
    try:
        target_reshaped = np.full_like(true_labels, target_class)
        tp = np.count_nonzero((true_labels == target_reshaped) & (predicted_labels == target_reshaped))
        fn = np.count_nonzero((true_labels == target_reshaped) & (predicted_labels != target_reshaped))
        return tp / (tp + fn)
    except Exception as e:
        raise MetricsException(metric_name, additional_context=str(e))


def class_recall(name, info: CalculateRequest) -> float:
    """
    Calculate the recall for a given class. The labels/predictions provided must only be for
    one attribute of the predictions. Calculating recalls for multiple attributes will raise
    an exception
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return _calculate_recall(name, info.true_labels, info.predicted_labels, info.target_class)


def macro_recall(name, info: CalculateRequest) -> float:
    """
    Calculate the macro recall for all classes
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return sum(
            [
                _calculate_recall(name, info.true_labels, info.predicted_labels, c)
                for c in np.unique(info.true_labels)
            ]
        ) / len(np.unique(info.true_labels))


metric_to_fn = {
    "accuracy": accuracy,
    "class_precision": class_precision,
    "precision": macro_precision,
    "class_recall": class_recall,
    "recall": macro_recall
}
