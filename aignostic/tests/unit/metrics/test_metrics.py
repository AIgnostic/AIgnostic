from aignostic.metrics.metrics import metrics_app, MetricsException, is_valid_for_per_class_metrics
from aif360.datasets import BinaryLabelDataset
from aif360.metrics import ClassificationMetric
from fastapi.testclient import TestClient
import pytest
import numpy as np
import pandas as pd

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
        is_valid_for_per_class_metrics(
            "class_precision",
            [[2, 3], [0, 3], [2, 3], [2, 3], [0, 3], [2, 3], [0, 3], [0, 3]]
        )
    assert e.value.status_code == 500
    assert "Error during metric calculation: class_precision" in e.value.detail
    assert "Multiple attributes provided" in e.value.detail


def test_no_input_validity_check_fails():
    with pytest.raises(MetricsException) as e:
        is_valid_for_per_class_metrics(
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

def test_disparate_impact():
    # Sample data
    data = {
        'label': [1, 0, 1, 1, 0, 1, 0, 0],
        'protected_attr': [1, 0, 1, 1, 0, 1, 0, 0]  # 1 = unprivileged, 0 = privileged
    }
    predicted_data = {
        'label': [1, 0, 1, 0, 0, 1, 1, 0],  # Predicted labels
        'protected_attr': [1, 0, 1, 1, 0, 1, 0, 0]
    }

    # Convert to BinaryLabelDataset
    dataset = BinaryLabelDataset(
        favorable_label=1,
        unfavorable_label=0,
        df=pd.DataFrame(data),
        label_names=['label'],
        protected_attribute_names=['protected_attr']
    )

    classified_dataset = BinaryLabelDataset(
        favorable_label=1,
        unfavorable_label=0,
        df=pd.DataFrame(predicted_data),
        label_names=['label'],
        protected_attribute_names=['protected_attr']
    )

    # Define privileged and unprivileged groups
    privileged_groups = [{'protected_attr': 0}]
    unprivileged_groups = [{'protected_attr': 1}]

    # Compute metrics
    metric = ClassificationMetric(dataset, classified_dataset, unprivileged_groups, privileged_groups)
    disparate_impact_value = metric.disparate_impact()

    print(f"Disparate Impact: {disparate_impact_value}")
