import numpy as np
from aignostic.metrics.metrics import calculate_metrics


def test_calculate_metrics():
    """
        Test calculate_metrics calls all metrics
    """
    y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0])
    y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0])
    metrics = ["accuracy", "precision", "recall"]

    results = calculate_metrics(y_true, y_pred, metrics)
    assert "accuracy" in results and results["accuracy"] == 0.75
    assert "precision" in results and results["precision"] == 0.75
    assert "recall" in results and results["recall"] == 0.75


def test_only_calcs_specified_metrics():
    y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0])
    y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0])
    metrics = ["accuracy", "recall"]

    results = calculate_metrics(y_true, y_pred, metrics)
    assert "accuracy" in results
    assert "precision" not in results
    assert "recall" in results
