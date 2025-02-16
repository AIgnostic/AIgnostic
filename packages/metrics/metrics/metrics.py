"""
    This module contains the implementation of various metrics
    For now this is a placeholder for the metrics implementation
    Containing simply the accuracy, precision and recall metrics
    For a binary classification problem
"""

from typing import Any, Callable
from metrics.models import (
    CalculateRequest,
    MetricValues,
)
from sklearn.metrics import f1_score, roc_auc_score, mean_absolute_error as mae, mean_squared_error as mse, r2_score
from aif360.metrics import ClassificationMetric
from aif360.datasets import BinaryLabelDataset
import pandas as pd
import numpy as np


class MetricsException(Exception):
    detail: str

    def __init__(self, name, additional_context=None):
        self.detail = f"Error during metric calculation: {name}"
        if additional_context:
            self.detail += f"; {additional_context}"
        super().__init__(self.detail)


def is_valid_for_per_class_metrics(metric_name, true_labels):
    """
    Check if the input is valid for the given metric. Valid fn for precision, recall and F1 scoring
    """
    if len(true_labels) == 0:
        raise MetricsException(
            metric_name,
            additional_context="No labels provided - will lead to division by zero",
        )
    elif len(true_labels[0]) > 1:
        raise MetricsException(
            metric_name,
            additional_context=f"Multiple attributes provided - cannot calculate {metric_name}",
        )
    elif len(true_labels[0]) == 0:
        raise MetricsException(
            metric_name,
            additional_context=f"No attributes provided - cannot calculate {metric_name}",
        )


"""
    Performance metrics
"""


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
        tp = np.count_nonzero(
            (true_labels == target_reshaped) & (predicted_labels == target_reshaped)
        )
        fp = np.count_nonzero(
            (true_labels != target_reshaped) & (predicted_labels == target_reshaped)
        )
        return tp / (tp + fp) if (tp + fp) != 0 else 0
    except (ValueError, TypeError) as e:
        raise MetricsException(metric_name, additional_context=str(e))


def class_precision(name, info: CalculateRequest) -> float:
    """
    Calculate the precision for a given class. The labels/predictions provided must only be for
    one attribute of the predictions. Calculating precisions for multiple attributes will raise
    an exception
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return _calculate_precision(
        name, info.true_labels, info.predicted_labels, info.target_class
    )


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
        tp = np.count_nonzero(
            (true_labels == target_reshaped) & (predicted_labels == target_reshaped)
        )
        fn = np.count_nonzero(
            (true_labels == target_reshaped) & (predicted_labels != target_reshaped)
        )
        return tp / (tp + fn) if (tp + fn) != 0 else 0
    except Exception as e:
        raise MetricsException(metric_name, additional_context=str(e))


def class_recall(name, info: CalculateRequest) -> float:
    """
    Calculate the recall for a given class. The labels/predictions provided must only be for
    one attribute of the predictions. Calculating recalls for multiple attributes will raise
    an exception
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return _calculate_recall(
        name, info.true_labels, info.predicted_labels, info.target_class
    )


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


def class_f1(name, info: CalculateRequest) -> float:
    """
    Calculate the F1 score for a given class. The labels
    provided must only be for one attribute of the predictions.
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return f1_score(info.true_labels, info.predicted_labels)


def macro_f1(name, info: CalculateRequest) -> float:
    """
    Calculate the macro F1 score for all classes
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return f1_score(info.true_labels, info.predicted_labels, average="macro")


def roc_auc(name, info: CalculateRequest) -> float:
    """
    Calculate the ROC-AUC score.
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return roc_auc_score(info.true_labels, info.predicted_labels)


def mean_absolute_error(name, info: CalculateRequest) -> float:
    """
    Calculate the Mean Absolute Error (MAE).
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return mae(info.true_labels, info.predicted_labels)


def mean_squared_error(name, info: CalculateRequest) -> float:
    """
    Calculate the Mean Squared Error (MSE).
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return mse(info.true_labels, info.predicted_labels)


def r_squared(name, info: CalculateRequest) -> float:
    """
    Calculate the R-squared score.
    """
    is_valid_for_per_class_metrics(name, info.true_labels)
    return r2_score(info.true_labels, info.predicted_labels)


def _prepare_datasets(info: CalculateRequest):
    """
    Prepare the datasets required for fairness metric calculations.

    This function takes the true labels, predicted labels, and protected attributes from the
    CalculateRequest object and creates BinaryLabelDataset objects for both the true and predicted
    labels. These datasets are then used to calculate various fairness metrics.

    :param info: CalculateRequest - contains the true labels, predicted labels, and protected attributes.
    :return: tuple - a tuple containing the true labels dataset and the predicted labels dataset.
    """
    true_labels = np.array(info.true_labels).flatten()
    predicted_labels = np.array(info.predicted_labels).flatten()

    if not hasattr(info, "protected_attr") or info.protected_attr is None:
        raise ValueError("protected_attr is missing from the request.")

    protected_attrs = np.array(info.protected_attr).flatten()
    df_true = pd.DataFrame({"label": true_labels, "protected_attr": protected_attrs})
    df_pred = pd.DataFrame(
        {"label": predicted_labels, "protected_attr": protected_attrs}
    )

    dataset = BinaryLabelDataset(
        df=df_true, label_names=["label"], protected_attribute_names=["protected_attr"]
    )
    classified_dataset = BinaryLabelDataset(
        df=df_pred, label_names=["label"], protected_attribute_names=["protected_attr"]
    )  # predictions
    return dataset, classified_dataset


"""
    Fairness metrics
"""


def equalized_odds_difference(name, info: CalculateRequest) -> tuple:
    """
    Compute equalized odds difference from a CalculateRequest.

    Args:
        request: CalculateRequest object containing true labels, predicted labels, and protected attribute.

    Returns:
        fpr_diff: Absolute difference in false positive rates across groups.
        tpr_diff: Absolute difference in true positive rates across groups.
    """

    is_valid_for_per_class_metrics(name, info.true_labels)

    if info.true_labels is None or info.predicted_labels is None or info.protected_attr is None:
        raise ValueError("Missing required fields: true_labels, predicted_labels, or protected_attr")

    labels = info.true_labels
    predictions = info.predicted_labels
    groups = info.protected_attr

    def rate(cond, pred):
        return np.mean(pred[cond]) if np.any(cond) else 0.0

    fpr_1 = rate((labels == 0) & (groups == 1), predictions)
    fpr_0 = rate((labels == 0) & (groups == 0), predictions)
    tpr_1 = rate((labels == 1) & (groups == 1), predictions)
    tpr_0 = rate((labels == 1) & (groups == 0), predictions)

    return abs(fpr_1 - fpr_0), abs(tpr_1 - tpr_0)


def create_fairness_metric_fn(metric_fn: Callable[[ClassificationMetric], Any]):
    def wrapper(name: str, info: CalculateRequest) -> Any:
        try:
            dataset, classified_dataset = _prepare_datasets(info)
            metric = ClassificationMetric(
                dataset,
                classified_dataset,
                privileged_groups=info.privileged_groups,
                unprivileged_groups=info.unprivileged_groups,
            )

            metrics = metric_fn(metric)
            if np.isnan(metrics):
                metrics = 0
            return metrics
        except Exception as e:
            raise MetricsException(name, additional_context=str(e))

    return wrapper


metric_to_fn = {
    "accuracy": accuracy,
    "class_precision": class_precision,
    "precision": macro_precision,
    "class_recall": class_recall,
    "recall": macro_recall,
    "class_f1_score": class_f1,
    "f1_score": macro_f1,
    "roc_auc": roc_auc,
    "mean_absolute_error": mean_absolute_error,
    "mean_squared_error": mean_squared_error,
    "r_squared": r_squared,
    "equalized_odds_difference": equalized_odds_difference,
    **{
        metric_name: create_fairness_metric_fn(
            # name=metric_name needed here otherwise metric_name will be captured by the lambda once
            lambda metric, name=metric_name: getattr(metric, name)()
        )
        for metric_name in [
            # aif360 fairness metrics
            "statistical_parity_difference",    # demographic parity
            # "equalized_odds_difference",        # doesn't exist
            "equal_opportunity_difference",
            "disparate_impact",
            "false_negative_rate_difference",
            "negative_predictive_value",
            "positive_predictive_value",
            "true_positive_rate_difference",
        ]
    },
}
""" Mapping of metric names to their corresponding functions"""


def calculate_metrics(info: CalculateRequest) -> MetricValues:
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
