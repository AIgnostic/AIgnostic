from aignostic.pydantic_models.metric_models import CalculateRequest, MetricsInfo, MetricValues

"""
    This module contains the implementation of various metrics
    For now this is a placeholder for the metrics implementation
    Containing simply the accuracy, precision and recall metrics
    For a binary classification problem
"""

import numpy as np
from fastapi import FastAPI, HTTPException
import math
from aif360.metrics import ClassificationMetric
from aif360.datasets import BinaryLabelDataset
import pandas as pd

metrics_app = FastAPI()

task_to_metric_map = {
    "binary_classification": [
        "disparate_impact",
        "equal_opportunity_difference",
        "equalized_odd_difference", 
        "false_negative_rate_difference",
    ],
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
        if metric not in metric_to_fn.keys():
            results[metric] = 1
        else:
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

def _prepare_datasets(info: CalculateRequest):
    true_labels = np.array(info.true_labels).flatten()
    predicted_labels = np.array(info.predicted_labels).flatten()

    if not hasattr(info, "protected_attr") or info.protected_attr is None:
        raise ValueError("protected_attr is missing from the request.")

    protected_attrs = np.array(info.protected_attr).flatten()
    df_true = pd.DataFrame({'label': true_labels, 'protected_attr': protected_attrs})
    df_pred = pd.DataFrame({'label': predicted_labels, 'protected_attr': protected_attrs})

    dataset = BinaryLabelDataset(df=df_true, label_names=['label'], protected_attribute_names=['protected_attr'])
    classified_dataset = BinaryLabelDataset(df=df_pred, label_names=['label'], protected_attribute_names=['protected_attr'])

    return dataset, classified_dataset


def disparate_impact(name, info: CalculateRequest) -> float:
    """
    Calculate the disparate impact of the model.
    """
    try:
        dataset, classified_dataset = _prepare_datasets(info)
        metric = ClassificationMetric(dataset, classified_dataset, 
                                      privileged_groups=info.privileged_groups,
                                      unprivileged_groups=info.unprivileged_groups)
        return metric.disparate_impact()

    except Exception as e:
        raise MetricsException(name, additional_context=str(e))


def equal_opportunity_difference(name, info: CalculateRequest) -> float:
    """
    Calculate the equalized odds difference of the model
    """
    try:
        dataset, classified_dataset = _prepare_datasets(info)
        metric = ClassificationMetric(dataset, classified_dataset, 
                                      privileged_groups=info.privileged_groups,
                                      unprivileged_groups=info.unprivileged_groups)
        eod_value = metric.equal_opportunity_difference()
        return eod_value

    except Exception as e:
        raise MetricsException(name, additional_context=str(e))


def equalized_odds_difference(name, info: CalculateRequest) -> float:
    """
    Calculate the equalized odds difference of the model
    """
    try:
        dataset, classified_dataset = _prepare_datasets(info)
        metric = ClassificationMetric(dataset, classified_dataset, 
                                      privileged_groups=info.privileged_groups,
                                      unprivileged_groups=info.unprivileged_groups)
        return metric.equalized_odds_difference()

    except Exception as e:
        raise MetricsException(name, additional_context=str(e))


def false_negative_rate_difference(name, info: CalculateRequest) -> float:
    """
    Calculate the false negative rate difference of the model
    """
    try:
        dataset, classified_dataset = _prepare_datasets(info)
        metric = ClassificationMetric(dataset, classified_dataset,
                                      privileged_groups=info.privileged_groups,
                                      unprivileged_groups=info.unprivileged_groups)
        return metric.false_negative_rate_difference()
    except Exception as e:
        raise MetricsException(name, additional_context=str(e))

# def negative_predictive_value(name, info: CalculateRequest) -> float:
#     """
#     Calculate the negative predictive value of the model
#     """
#     try:
#         # Calculate the negative predictive value
#         return 0
#     except Exception as e:
#         # Catch exceptions generally for now rather than specific ones
#         raise MetricsException(name, additional_context=str(e))
    
# def positive_predictive_value(name, info: CalculateRequest) -> float:
#     """
#     Calculate the positive predictive value of the model
#     """
#     try:
#         # Calculate the positive predictive value
#         return 0
#     except Exception as e:
#         # Catch exceptions generally for now rather than specific ones
#         raise MetricsException(name, additional_context=str(e))
    
# def statistical_parity_difference(name, info: CalculateRequest) -> float:
#     """
#     Calculate the statistical parity difference of the model
#     """
#     try:
#         # Calculate the statistical parity difference
#         return 0
#     except Exception as e:
#         # Catch exceptions generally for now rather than specific ones
#         raise MetricsException(name, additional_context=str(e))

# def true_positive_rate_difference(name, info: CalculateRequest) -> float:
#     """
#     Calculate the true positive rate difference of the model
#     """
#     try:
#         # Calculate the true positive rate difference
#         return 0
#     except Exception as e:
#         # Catch exceptions generally for now rather than specific ones
#         raise MetricsException(name, additional_context=str(e))

metric_to_fn = {
    "accuracy": accuracy,
    "class_precision": class_precision,
    "precision": macro_precision,
    "class_recall": class_recall,
    "recall": macro_recall,
    # AIF360 Fairnes metrics
    "disparate_impact": disparate_impact,
    "equal_opportunity_difference": equal_opportunity_difference,
    "equalized_odds_difference": equalized_odds_difference,
    "false_negative_rate_difference": false_negative_rate_difference,
    # "negative_predictive_value": negative_predictive_value,
    # "positive_predictive_value": positive_predictive_value,
    # "statistical_parity_difference": statistical_parity_difference,
    # "true_positive_rate_difference": true_positive_rate_difference
}
