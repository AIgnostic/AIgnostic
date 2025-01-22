"""
    This module contains the implementation of various metrics
    For now this is a placeholder for the metrics implementation
    Containing simply the accuracy, precision and recall metrics
    For a binary classification problem
"""

import numpy as np


def calculate_metrics(y_true, y_pred, metrics):
    """
        Calculate the metrics for the given y_true and y_pred
        Args:
            y_true: list of true labels
            y_pred: list of predicted labels
            metrics: list of metric functions e.g. "accuracy", "precision"
    """
    print("Y_TRUE", y_true)
    print("Y_PRED", y_pred)
    print("METRICS", metrics)

    try:
        results = {}
        for metric in metrics:
            results[metric] = globals()[metric](np.array(y_true), np.array(y_pred))

        return results
    except Exception as e:
        print("Error while calculating metrics:", e)
        return None


def accuracy(y_true, y_pred):
    return (y_true == y_pred).mean()


def precision(y_true, y_pred):
    precisions = [per_class_precision(y_true, y_pred, c) for c in np.unique(y_true)]
    return np.mean(precisions)


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
