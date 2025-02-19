from threading import Thread
import pytest
from mocks.dataset.mock_server import app as client_mock
from api.dataset.validate_dataset_api import app as server_app
from mocks.api_utils import MOCK_DATASET_API_KEY
import uvicorn
import time
from api.pydantic_models.data_models import FetchDatasetRequest
from fastapi.testclient import TestClient

app_client = TestClient(server_app)

valid_dataset_url = "http://127.0.0.1:3333/fetch-datapoints"
invalid_format_url = "http://127.0.0.1:3333/invalid-data-format"
not_found_url = "http://127.0.0.1:3333/not-found-url"


@pytest.fixture(scope="module")
def run_servers():
    data_config = uvicorn.Config(app=client_mock, host="127.0.0.1", port=3333)
    data_server = uvicorn.Server(data_config)

    def start_server(server):
        server.run()

    thread = Thread(target=start_server, args=(data_server,))
    thread.start()

    time.sleep(2)  # Wait for the servers to start
    assert data_server.started

    yield

    data_server.should_exit = True

    thread.join()


def test_correct_apis_do_not_err(run_servers):
    fetch_dataset_request = FetchDatasetRequest(
        dataset_url=valid_dataset_url,
        dataset_api_key=MOCK_DATASET_API_KEY
    )
    response = app_client.post("/fetch-data", json=fetch_dataset_request.model_dump(mode="json"))
    assert response.status_code == 200, response
    assert len(response.json()["features"]) == 2
    assert len(response.json()["labels"]) == 2
    assert len(response.json()["group_ids"]) == 2


def test_server_returns_400_error_given_invalid_data_format(run_servers):
    fetch_dataset_request = FetchDatasetRequest(
        dataset_url=invalid_format_url,
        dataset_api_key=MOCK_DATASET_API_KEY
    )
    response = app_client.post("/fetch-data", json=fetch_dataset_request.model_dump(mode="json"))
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Error while validating data: All feature rows must have the same number of elements."
    }


def test_non_existent_endpoint_throws_404(run_servers):
    fetch_dataset_request = FetchDatasetRequest(
        dataset_url=not_found_url,
        dataset_api_key=MOCK_DATASET_API_KEY
    )
    response = app_client.post("/fetch-data", json=fetch_dataset_request.model_dump(mode="json"))
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
