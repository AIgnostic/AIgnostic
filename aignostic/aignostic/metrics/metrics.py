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
            detail += f"\n{additional_context}"
        super().__init__(
            status_code=500,
            detail=detail
        )


def accuracy(name, info: CalculateRequest):
    try:
        return (info.true_labels == info.predicted_labels).mean()
    except Exception as e:
        # Catch exceptions generally for now rather than specific ones
        raise MetricsException(name, additional_context=str(e))


metric_to_fn = {
    "accuracy": accuracy#,
    # "precision": precision
}



def recall(y_true, y_pred):
    recalls = [per_class_recall(y_true, y_pred, c) for c in np.unique(y_true)]
    return np.mean(recalls)


def per_class_recall(y_true, y_pred, c):
    tp = ((y_true == c) & (y_pred == c)).sum()
    fn = ((y_true == c) & (y_pred != c)).sum()
    return tp / (tp + fn)


def per_class_precision(y_true, y_pred, c):
    tp = ((y_true == c) & (y_pred == c)).sum()
    fp = ((y_true != c) & (y_pred == c)).sum()
    return tp / (tp + fp)

# def precision(y_true, y_pred):
#     precisions = [per_class_precision(y_true, y_pred, c) for c in np.unique(y_true)]
#     return np.mean(precisions)