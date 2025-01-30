import numpy as np
from aignostic.metrics.metrics import calculate_metrics, metrics_app, MetricsException
from fastapi.testclient import TestClient
import pytest

metrics_client = TestClient(metrics_app)


def test_accuracy():
    response = metrics_client.post("/calculate-metrics", json={
        "metrics": ["accuracy"],
        "true_labels": [[1], [0], [1], [1], [0], [1], [0], [0]],
        "predicted_labels": [[1], [0], [1], [0], [0], [1], [1], [0]],
    })
    assert response.status_code == 200, response.text
    assert response.json() == {"metric_values": {"accuracy": 0.75}}, response.json()


def test_precision():
    response = metrics_client.post("/calculate-metrics", json={
        "metrics": ["class_precision"],
        "true_labels": [[2], [0], [2], [2], [0], [2], [0], [0]],
        "predicted_labels": [[2], [0], [2], [0], [0], [2], [2], [2]],
        "target_class": 2
    })
    print(response.json())
    assert response.status_code == 200, response.text
    assert response.json() == {"metric_values": {"class_precision": 0.6}}, response.json()


def test_multi_attribute_precision_per_class_fails():
    response = metrics_client.post("/calculate-metrics", json={
        "metrics": ["class_precision"],
        "true_labels": [[2, 3], [0, 3], [2, 3], [2, 3], [0, 3], [2, 3], [0, 3], [0, 3]],
        "predicted_labels": [[2, 3], [0, 3], [2, 3], [0, 3], [0, 3], [2, 3], [2, 3], [2, 3]],
    })
    assert response.status_code == 500
    assert "Error during metric calculation: class_precision" in response.text
    assert "Multiple attributes provided" in response.text


def test_no_input_precision_fails():
    response = metrics_client.post("/calculate-metrics", json={
        "metrics": ["class_precision"],
        "true_labels": [],
        "predicted_labels": [],
        "target_class": 2
    })
    assert response.status_code == 500
    assert "Error during metric calculation: class_precision" in response.text
    assert "No labels provided" in response.text


def test_macro_precision():
    response = metrics_client.post("/calculate-metrics", json={
        "metrics": ["precision"],
        "true_labels": [[2], [0], [2], [2], [0], [2], [0], [0]],
        "predicted_labels": [[2], [0], [2], [0], [0], [2], [2], [2]],
    })
    assert response.status_code == 200, response.text
    assert round(response.json()["metric_values"]["precision"], 7) == 0.6333333, response.json()


@pytest.mark.skip(reason="Files being updated/refactored")
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


@pytest.mark.skip(reason="Files being updated/refactored")
def test_only_calcs_specified_metrics():
    y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0])
    y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0])
    metrics = ["accuracy", "recall"]

    results = calculate_metrics(y_true, y_pred, metrics)
    assert "accuracy" in results
    assert "precision" not in results
    assert "recall" in results
