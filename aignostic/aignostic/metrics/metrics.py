"""
    This module contains the implementation of various metrics
    For now this is a placeholder for the metrics implementation
    Containing simply the accuracy, precision and recall metrics
    For a binary classification problem
"""

import numpy as np
from abc import abstractmethod
from fastapi import FastAPI

metrics_app = FastAPI()

task_to_metric_map = {
    "binary_classification": [],
    "multi_class_classification": [],
    "regression": []
}

@metrics_app.get("/retrieve-metric-info")
def retrieve_info():
    
    pass


@metrics_app.get("/calculate-metrics")
def calculate_metrics(y_true, y_pred, metrics):
    """
    Calculate the metrics for the given y_true and y_pred

    Params:
        y_true: list of true labels
        y_pred: list of predicted labels
        metrics: list of metric functions e.g. "accuracy", "precision"
    """
    try:
        results = {}
        for metric in metrics:
            results[metric] = globals()[metric](np.array(y_true), np.array(y_pred))

        return results
    except Exception as e:
        print("Error while calculating metrics:", e)
        return None


class Metric():
    def __init__(self, name, method):
        self.name = name
        self.method = method
        self.value = None
    
    @abstractmethod
    def calculate(self, *args, **kwargs):
        pass


class BinaryClassificationMetric(Metric):
    def __init__(self, name, calculate_fn):
        super().__init__(name)
        self.calculate_fn = calculate_fn
        self.value = None
    
    @abstractmethod
    def calculate(self, y_true, y_pred):
        """
        Calculate the metric for the given y_true and y_pred
        @param y_true: list of true labels
        @param y_pred: list of predicted labels
        """
        self.value = self.calculate_fn(y_true, y_pred)
        return self.value


accuracy = BinaryClassificationMetric(
    "accuracy",
    lambda y_true, y_pred: (y_true == y_pred).mean()
)    


precision = BinaryClassificationMetric(
    "precision",
    lambda y_true, y_pred: per_class_precision(y_true, y_pred, 1)
)




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
