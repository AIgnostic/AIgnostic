import numpy as np
from aignostic.metrics.metrics import calculate_metrics, metrics_app
from fastapi.testclient import TestClient
import pytest

metrics_client = TestClient(metrics_app)


def test_accuracy():
    response = metrics_client.post("/calculate-metrics", json={
        "metrics": ["accuracy"],
        "true_labels": [[1, 0, 1, 1, 0, 1, 0, 0]],
        "predicted_labels": [[1, 0, 1, 0, 0, 1, 1, 0]]
    })
    print(response.json())
    print(response.text)
    assert response.status_code == 200, response.text
    assert response.json() == {"metric_values": {"accuracy": 0.75}}, response.json()


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
