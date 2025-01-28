from threading import Thread
import pytest
from aignostic.router.api import api
from tests.utils.dataset.mock_server import app as data_app
from tests.utils.model.scikit_mock import app as sk_model_app
from tests.utils.api_utils import MOCK_DATASET_API_KEY, MOCK_MODEL_API_KEY
import uvicorn
import time
from fastapi.testclient import TestClient
from fastapi import HTTPException
from requests.exceptions import HTTPError

app_client = TestClient(api)


data_url = "http://127.0.0.1:3333/fetch-datapoints"
model_url = "http://127.0.0.1:3334/predict"
metrics = ["accuracy", "precision", "recall"]


@pytest.fixture(scope="module")
def run_servers():
    data_config = uvicorn.Config(app=data_app, host="127.0.0.1", port=3333)
    model_config = uvicorn.Config(app=sk_model_app, host="127.0.0.1", port=3334)
    app_config = uvicorn.Config(app=app_client, host="127.0.0.1", port=3335)
    data_server = uvicorn.Server(data_config)
    model_server = uvicorn.Server(model_config)
    app_server = uvicorn.Server(app_config)

    def start_server(server):
        server.run()

    threads = [Thread(target=start_server, args=(server,)) for server in [data_server, model_server, app_server]]
    for thread in threads:
        thread.start()

    time.sleep(2)  # Wait for the servers to start
    assert data_server.started
    assert model_server.started
    assert app_server.started

    yield

    data_server.should_exit = True
    model_server.should_exit = True
    app_server.should_exit = True

    for thread in threads:
        thread.join()


def test_correct_apis_do_not_err(run_servers):
    response = app_client.post("/evaluate", json={
        "data_url": data_url,
        "model_url": model_url,
        "metrics": metrics,
        "model_api_key": MOCK_MODEL_API_KEY,
        "data_api_key": MOCK_DATASET_API_KEY
    })
    # Useful debug messages
    print(response.text)
    print(response.status_code)
    print(response.headers)
    print(response.url)
    assert response.status_code == 200, response


def test_incorrect_dataset_api_throws_401():
    try:
        response = app_client.post("/evaluate", json={
            "data_url": data_url,
            "model_url": model_url,
            "metrics": metrics,
            "model_api_key": MOCK_MODEL_API_KEY,
            "data_api_key": MOCK_DATASET_API_KEY + "1"
        })
        assert False, f"Should have thrown 401, but a response was received instead. Response: {response}"
    except HTTPException as e:
        assert e.status_code == 401, e


def test_incorrect_model_api_throws_401():
    try:
        response = app_client.post("/evaluate", json={
            "data_url": data_url,
            "model_url": model_url,
            "metrics": metrics,
            "model_api_key": MOCK_MODEL_API_KEY + "1",
            "data_api_key": MOCK_DATASET_API_KEY
        })
        assert False, f"Should have thrown 401, but a response was received instead. Response: {response}"
    except HTTPException as e:
        assert e.status_code == 401, e
