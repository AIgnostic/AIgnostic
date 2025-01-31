from fastapi.testclient import TestClient
from tests.utils.api_utils import MOCK_DATASET_API_KEY
from tests.utils.dataset.mock_server import app as client_mock
from aignostic.dataset.validate_dataset_api import app as server_app

server_app = TestClient(server_app)
client_mock = TestClient(client_mock)

local_server = "http://127.0.0.1:5000"
valid_api_key = {"Authorization": f"Bearer {MOCK_DATASET_API_KEY}"}
invalid_api_key = {"Authorization": "Bearer INVALID_KEY"}


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
    assert len(data["features"]) == len(data["labels"]) == len(data["group_ids"]) == 2


def test_fetch_datapoints_given_n_of_50_returns_correctly():
    response = client_mock.get("/fetch-datapoints", headers=valid_api_key, params={"n": 50})
    assert response.status_code == 200
    data = response.json()
    assert "features" in data and "labels" in data and "group_ids" in data
    assert len(data["features"]) == len(data["labels"]) == len(data["group_ids"]) == 50
    # Check that the features are unique
    assert len(set(tuple(row) for row in data["features"])) == 50
