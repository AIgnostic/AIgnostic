from fastapi.testclient import TestClient
from mocks.api_utils import MOCK_DATASET_API_KEY
from mocks.dataset.mock_server import app as client_mock
from api.dataset.validate_dataset_api import _validate_dataset_format
from common.models import DatasetResponse
import pytest

client_mock = TestClient(client_mock)

valid_api_key = {"Authorization": f"Bearer {MOCK_DATASET_API_KEY}"}
invalid_api_key = {"Authorization": "Bearer INVALID_KEY"}


def test_read_root():
    response = client_mock.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Folktables data server!"}


def test_client_non_existent_endpoint_throws_404():
    response = client_mock.get("/hello")
    assert response.status_code == 404, response.text


def test_client_returns_data_given_valid_api_key():
    response = client_mock.get("/fetch-datapoints", headers=valid_api_key)
    assert response.status_code == 200
    assert response.json() != {}


def test_client_given_invalid_api_key_throws_401():
    response = client_mock.get("/fetch-datapoints", headers=invalid_api_key)
    assert response.status_code == 401
    assert response.json() != {}
    assert response.json()["detail"] == "Unauthorized access: Please check your API Key"


def test_fetch_datapoints_returns_correctly():
    response = client_mock.get("/fetch-datapoints", headers=valid_api_key)
    assert response.status_code == 200
    data = response.json()
    assert "features" in data and "labels" in data and "group_ids" in data
    print("data: ", data)
    assert len(data["features"]) == len(data["labels"]) == len(data["group_ids"]) == 2


def test_fetch_datapoints_given_n_of_50_returns_correctly():
    response = client_mock.get("/fetch-datapoints", headers=valid_api_key, params={"n": 50})
    assert response.status_code == 200
    data = response.json()
    assert "features" in data and "labels" in data and "group_ids" in data
    assert len(data["features"]) == len(data["labels"]) == len(data["group_ids"]) == 50


# Test validation function
def test_valid_dataset():
    valid_data = {
        "features": [[1, 2, 3], [4, 5, 6]],
        "labels": [[0], [1]],
        "group_ids": [1, 2]
    }
    result = _validate_dataset_format(valid_data)
    assert isinstance(result, DatasetResponse)


def test_mismatched_list_lengths():
    invalid_data = {
        "features": [[1, 2, 3], [4, 5, 6]],
        "labels": [[0]],  # Different length
        "group_ids": [1, 2]
    }
    with pytest.raises(ValueError, match="Features, labels, and group_ids must have the same number of rows"):
        _validate_dataset_format(invalid_data)


def test_inconsistent_feature_row_lengths():
    invalid_data = {
        "features": [[1, 2, 3], [4, 5]],  # Different row length
        "labels": [[0], [1]],
        "group_ids": [1, 2]
    }
    with pytest.raises(ValueError, match="All feature rows must have the same number of elements"):
        _validate_dataset_format(invalid_data)


def test_inconsistent_label_row_lengths():
    invalid_data = {
        "features": [[1, 2, 3], [4, 5, 6]],
        "labels": [[0], [1, 2]],  # Different row length
        "group_ids": [1, 2]
    }
    with pytest.raises(ValueError, match="All label rows must have the same number of elements"):
        _validate_dataset_format(invalid_data)


def test_empty_dataset():
    empty_data = {
        "features": [],
        "labels": [],
        "group_ids": []
    }
    result = _validate_dataset_format(empty_data)
    assert isinstance(result, DatasetResponse)


def test_invalid_data_type():
    invalid_data = "invalid_string"
    with pytest.raises(TypeError):  # Pydantic should fail here
        _validate_dataset_format(invalid_data)


def test_invalid_model_structure():
    invalid_data = {
        "features": "not a list",
        "labels": "not a list",
        "group_ids": "not a list"
    }
    with pytest.raises(ValueError):
        _validate_dataset_format(invalid_data)
