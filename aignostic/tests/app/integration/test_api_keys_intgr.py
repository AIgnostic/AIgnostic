from threading import Thread
import pytest
from aignostic.router.api import api, generate_metrics_from_info, DatasetRequest
from tests.dataset_api.unit.mock_server import app as data_mock
from tests.dataset_api.unit.mock_server import MOCK_API_KEY as DATASET_API
from tests.model_api.model.scikit_mock import app as model_mock
from tests.model_api.model.scikit_mock import MOCK_API_KEY as MODEL_API
import uvicorn
from fastapi.testclient import TestClient

data_mock = TestClient(data_mock)
model_mock = TestClient(model_mock)
api_mock = TestClient(api)


data_url = "http://127.0.0.1:3333/fetch-datapoints"
model_url = "http://127.0.0.1:3334/predict"
metrics = ["accuracy", "precision", "recall"]

@pytest.fixture(scope="module")
def run_servers():
    data_config = uvicorn.Config(app=data_mock, host="127.0.0.1", port=3333)
    model_config = uvicorn.Config(app=model_mock, host="127.0.0.1", port=3334)
    app_config = uvicorn.Config(app=api, host="127.0.0.1", port=3335)
    data_server = uvicorn.Server(data_config)
    model_server = uvicorn.Server(model_config)
    app_server = uvicorn.Server(app_config)

    def start_servers():
        nonlocal data_server, model_server, app_server
        data_server.run()
        model_server.run()
        app_server.run()
    thread = Thread(target=start_servers)
    thread.start()
    yield
    data_server.should_exit = True
    model_server.should_exit = True
    app_server.should_exit = True
    thread.join()

@pytest.mark.asyncio
async def test_correct_apis_do_not_err(run_servers):
    response = await generate_metrics_from_info(
        {
            "datasetURL": data_url,
            "modelURL": model_url,
            "modelAPIKey": MODEL_API,
            "datasetAPIKey": DATASET_API,
            "metrics": metrics
        }
    )
    assert response.status_code == 200, response

@pytest.mark.skip(reason="Error Codes and Messages are yet to be implemented")
def test_incorrect_dataset_api_throws_401():
    pass


@pytest.mark.skip(reason="Error Codes and Messages are yet to be implemented")
def test_incorrect_model_api_throws_401():
    pass