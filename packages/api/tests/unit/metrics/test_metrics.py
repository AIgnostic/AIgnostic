from api.metrics.metrics import (
    metrics_app,
    MetricsException,
)
from metrics.metrics import is_valid_for_per_class_metrics
from fastapi.testclient import TestClient
import pytest

metrics_client = TestClient(metrics_app)


# Test Data Function
def json_text(metric_name):
    return {
        "metrics": [metric_name],
        "true_labels": [[1], [0], [1], [1], [0], [1], [0], [1]],
        "predicted_labels": [[1], [0], [0], [0], [1], [0], [1], [0]],
        "privileged_groups": [{"protected_attr": 1}],
        "unprivileged_groups": [{"protected_attr": 0}],
        "protected_attr": [0, 1, 0, 0, 1, 0, 1, 1],
    }


def test_accuracy():
    response = metrics_client.post(
        "/calculate-metrics",
        json={
            "metrics": ["accuracy"],
            "true_labels": [[1], [0], [1], [1], [0], [1], [0], [0]],
            "predicted_labels": [[1], [0], [1], [0], [0], [1], [1], [0]],
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {"metric_values": {"accuracy": 0.75}}, response.json()


def test_multi_attribute_validity_check_fails():
    with pytest.raises(MetricsException) as e:
        is_valid_for_per_class_metrics(
            "class_precision",
            [[2, 3], [0, 3], [2, 3], [2, 3], [0, 3], [2, 3], [0, 3], [0, 3]],
        )
    assert e.value.status_code == 500
    assert "Error during metric calculation: class_precision" in e.value.detail
    assert "Multiple attributes provided" in e.value.detail


def test_no_input_validity_check_fails():
    with pytest.raises(MetricsException) as e:
        is_valid_for_per_class_metrics("class_precision", [])
    assert e.value.status_code == 500
    assert "Error during metric calculation: class_precision" in e.value.detail
    assert "No labels provided" in e.value.detail


# Test a random metric to make sure it works


def test_precision():
    response = metrics_client.post(
        "/calculate-metrics",
        json={
            "metrics": ["class_precision"],
            "true_labels": [[2], [0], [2], [2], [0], [2], [0], [0]],
            "predicted_labels": [[2], [0], [2], [0], [0], [2], [2], [2]],
            "target_class": 2,
        },
    )
    print(response.json())
    assert response.status_code == 200, response.text
    assert response.json() == {
        "metric_values": {"class_precision": 0.6}
    }, response.json()


def test_multiple_metrics():
    response = metrics_client.post(
        "/calculate-metrics",
        json={
            "metrics": ["accuracy", "class_precision", "class_recall"],
            "true_labels": [[2], [0], [2], [2], [0], [2], [0], [0]],
            "predicted_labels": [[2], [0], [2], [0], [0], [2], [2], [2]],
            "target_class": 2,
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        "metric_values": {
            "accuracy": 0.625,
            "class_precision": 0.6,
            "class_recall": 0.75,
        }
    }, response.json()


def test_multiple_binary_classifier_metrics():
    response = metrics_client.post(
        "/calculate-metrics",
        json={
            "metrics": [
                "disparate_impact",
                "equal_opportunity_difference",
                "equalized_odds_difference",
            ],
            "true_labels": [[1], [0], [1], [1], [0], [1], [0], [0]],
            "predicted_labels": [[1], [0], [1], [1], [0], [1], [1], [1]],
            "privileged_groups": [{"protected_attr": 1}],
            "unprivileged_groups": [{"protected_attr": 0}],
            "protected_attr": [0, 1, 0, 0, 1, 0, 1, 1],
            "target_class": 2,
        },
    )
    assert response.status_code == 200, response.text
    expected_metrics = {
        "disparate_impact": 2.0,
        "equal_opportunity_difference": 0.0,
        "equalized_odds_difference": 0.0,
    }
    for metric, value in expected_metrics.items():
        assert round(response.json()["metric_values"][metric], 7) == round(
            value, 7
        ), f"{metric} failed"


def test_error_if_no_protected_attrs():
    req = json_text("disparate_impact")
    del req["protected_attr"]
    response = metrics_client.post("/calculate-metrics", json=req)

    assert response.status_code == 500, response.text
    assert "protected_attr" in response.json()["detail"]
    assert "missing" in response.json()["detail"]
