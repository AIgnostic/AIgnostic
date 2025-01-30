import numpy as np
from aignostic.metrics.metrics import calculate_metrics, metrics_app, MetricsException, check_valid_input
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


def test_multi_attribute_validity_check_fails():
    with pytest.raises(MetricsException) as e:
        check_valid_input(
            "class_precision",
            [[2, 3], [0, 3], [2, 3], [2, 3], [0, 3], [2, 3], [0, 3], [0, 3]]
        )
    assert e.value.status_code == 500
    assert "Error during metric calculation: class_precision" in e.value.detail
    assert "Multiple attributes provided" in e.value.detail


def test_no_input_validity_check_fails():
    with pytest.raises(MetricsException) as e:
        check_valid_input(
            "class_precision",
            []
        )
    assert e.value.status_code == 500
    assert "Error during metric calculation: class_precision" in e.value.detail
    assert "No labels provided" in e.value.detail


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


def test_macro_precision():
    response = metrics_client.post("/calculate-metrics", json={
        "metrics": ["precision"],
        "true_labels": [[2], [0], [2], [2], [0], [2], [0], [0]],
        "predicted_labels": [[2], [0], [2], [0], [0], [2], [2], [2]],
    })
    assert response.status_code == 200, response.text
    assert round(response.json()["metric_values"]["precision"], 7) == 0.6333333, response.json()


def test_recall():
    response = metrics_client.post("/calculate-metrics", json={
        "metrics": ["class_recall"],
        "true_labels": [[2], [0], [2], [2], [0], [2], [0], [0]],
        "predicted_labels": [[2], [0], [2], [0], [0], [2], [2], [2]],
        "target_class": 2
    })
    assert response.status_code == 200, response.text
    assert response.json() == {"metric_values": {"class_recall": 0.75}}, response.json()


def test_macro_recall():
    response = metrics_client.post("/calculate-metrics", json={
        "metrics": ["recall"],
        "true_labels": [[2], [0], [2], [2], [0], [2], [0], [0]],
        "predicted_labels": [[2], [0], [2], [0], [0], [2], [2], [2]],
    })
    assert response.status_code == 200, response.text
    assert response.json() == {"metric_values": {"recall": 0.625}}, response.json()
        

def test_multiple_metrics():
    response = metrics_client.post("/calculate-metrics", json={
        "metrics": ["accuracy", "class_precision", "class_recall"],
        "true_labels": [[2], [0], [2], [2], [0], [2], [0], [0]],
        "predicted_labels": [[2], [0], [2], [0], [0], [2], [2], [2]],
        "target_class": 2
    })
    assert response.status_code == 200, response.text
    assert response.json() == {
        "metric_values": {
            "accuracy": 0.625,
            "class_precision": 0.6,
            "class_recall": 0.75
        }
    }, response.json()
