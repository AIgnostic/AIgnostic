from aignostic.pydantic_models.metric_models import CalculateRequest, MetricsInfo, MetricValues

"""
    This module contains the implementation of various metrics
    For now this is a placeholder for the metrics implementation
    Containing simply the accuracy, precision and recall metrics
    For a binary classification problem
"""

import numpy as np
from abc import abstractmethod
from fastapi import FastAPI, HTTPException

metrics_app = FastAPI()

task_to_metric_map = {
    "binary_classification": [],
    "multi_class_classification": [],
    "regression": []
}


@metrics_app.get("/retrieve-metric-info", response_model=MetricsInfo)
def retrieve_info() -> MetricsInfo:
    return MetricsInfo(task_to_metric_map=task_to_metric_map)


@metrics_app.post("/calculate-metrics")
def calculate_metrics(info: CalculateRequest):
    """
    Calculate the metrics for the given y_true and y_pred

    Params:
        y_true: list of true labels
        y_pred: list of predicted labels
        metrics: list of metric functions e.g. "accuracy", "precision"
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


def accuracy(name, info: CalculateRequest) -> float:
    """
    Calculate the accuracy of the model
    """
    try:
        return (info.true_labels == info.predicted_labels).mean()
    except Exception as e:
        # Catch exceptions generally for now rather than specific ones
        raise MetricsException(name, additional_context=str(e))


def calculate_precision(true_labels, predicted_labels, target_class, metric_name=""):
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
    if len(info.true_labels) == 0:
        raise MetricsException(name, additional_context="No labels provided - will lead to division by zero")
    elif len(info.true_labels[0]) > 1:
        raise MetricsException(name, additional_context="Multiple attributes provided - cannot calculate precision")
    elif len(info.true_labels[0]) == 0:
        raise MetricsException(name, additional_context="No attributes provided - cannot calculate precision")

    return calculate_precision(info.true_labels, info.predicted_labels, info.target_class, name)


def macro_precision(name, info: CalculateRequest) -> float:
    """
    Calculate the macro precision for all classes
    """
    if len(info.true_labels) == 0:
        raise MetricsException(name, additional_context="No labels provided - will lead to division by zero")
    elif len(info.true_labels[0]) > 1:
        raise MetricsException(name, additional_context="Multiple attributes provided - cannot calculate precision")
    elif len(info.true_labels[0]) == 0:
        raise MetricsException(name, additional_context="No attributes provided - cannot calculate precision")

    return sum(
            [
                calculate_precision(info.true_labels, info.predicted_labels, c, name)
                for c in np.unique(info.true_labels)
            ]
        ) / len(np.unique(info.true_labels))


def recall_per_class(name, info: CalculateRequest) -> float:
    pass


def macro_recall(name, info: CalculateRequest) -> float:
    pass


metric_to_fn = {
    "accuracy": accuracy,
    "class_precision": class_precision,
    "precision": macro_precision,
    "recall_per_class": recall_per_class,
    "recall": macro_recall
}



def recall(y_true, y_pred):
    recalls = [per_class_recall(y_true, y_pred, c) for c in np.unique(y_true)]
    return np.mean(recalls)


def per_class_recall(y_true, y_pred, c):
    tp = ((y_true == c) & (y_pred == c)).sum()
    fn = ((y_true == c) & (y_pred != c)).sum()
    return tp / (tp + fn)

# def precision(y_true, y_pred):
#     precisions = [per_class_precision(y_true, y_pred, c) for c in np.unique(y_true)]
#     return np.mean(precisions)