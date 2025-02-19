from fastapi.testclient import TestClient
from mocks.dataset.mock_server import app as data_app
from mocks.model.scikit_mock import app as sk_model_app
from mocks.model.huggingface_binclassifier import app as hf_model_app
from mocks.api_utils import MOCK_DATASET_API_KEY, MOCK_MODEL_API_KEY

data_client = TestClient(data_app)
sk_model_client = TestClient(sk_model_app)
hf_model_client = TestClient(hf_model_app)


def test_correct_dataset_api_does_not_err():
    response = data_client.get("/fetch-datapoints", headers={"Authorization": f"Bearer {MOCK_DATASET_API_KEY}"})
    assert response.status_code == 200


def test_invalid_authorization_format_throws_403():
    response = data_client.get("/fetch-datapoints", headers={"Authorization": f"{MOCK_DATASET_API_KEY}"})
    assert response.status_code == 403


def test_incorrect_dataset_api_throws_401():
    response = data_client.get("/fetch-datapoints", headers={"Authorization": f"Bearer {MOCK_DATASET_API_KEY}1"})
    assert response.status_code == 401


def test_correct_model_api_does_not_err():
    response = sk_model_client.post("/predict", json={
        "features": [],
        "labels": [],
        "group_ids": []
    }, headers={"Authorization": f"Bearer {MOCK_MODEL_API_KEY}"})
    assert response.status_code == 200


def test_incorrect_model_api_throws_401():
    response = sk_model_client.post("/predict", json={
        "features": [],
        "labels": [],
        "group_ids": []
    }, headers={"Authorization": f"Bearer {MOCK_MODEL_API_KEY}1"})
    assert response.status_code == 401


def test_model_not_requiring_key_succeeds():
    response = hf_model_client.post("/predict", json={
        "features": [],
        "labels": [],
        "group_ids": []
    })
    assert response.status_code == 200
