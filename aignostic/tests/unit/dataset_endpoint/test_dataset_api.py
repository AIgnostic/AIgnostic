from fastapi.testclient import TestClient
from tests.utils.dataset.mock_server import app as client_mock
from tests.utils.api_utils import MOCK_DATASET_API_KEY
from aignostic.dataset.validate_dataset_api import app as server_mock
import pytest

server_mock = TestClient(server_mock)
client_mock = TestClient(client_mock)

local_server = "http://127.0.0.1:5000"
valid_url = local_server + "/fetch-datapoints"
unexpected_data_url = local_server + "/invalid-data"
invalid_url = local_server + "/invalid-url"


# Client tests
def test_client_returns_data():
    print(MOCK_DATASET_API_KEY)
    response = client_mock.get("/fetch-datapoints", headers={"Authorization": f"Bearer {MOCK_DATASET_API_KEY}"})
    assert response.status_code == 200
    assert response.json() != {}


@pytest.mark.skip(reason="Not implemented - possibly should be moved to the app folder for unit testing")
def test_invalid_data_is_handled_correctly():
    pass

# # Server tests
# @pytest.fixture(scope="module")
# def start_mock_server():
#     import uvicorn
#     config = uvicorn.Config(app=client_mock, host="127.0.0.1", port=5000)
#     server = uvicorn.Server(config)

#     def run_mock_server():
#         nonlocal server
#         server.run()

#     thread = Thread(target=run_mock_server)
#     thread.start()
#     yield
#     server.should_exit = True
#     thread.join()


# def test_server_validates_client_dataset_correctly_given_valid_url(start_mock_server):
#     response = server_mock.get("/validate-dataset?url=" + valid_url)
#     assert response.status_code == 200
#     assert len(response.json()["columns"]) == len(expected_ACS_column_names)
#     assert response.json()["columns"] == expected_ACS_column_names
#     assert response.json()["rows"] == 2


# def test_server_returns_400_error_given_unexpected_data_format(start_mock_server):
#     response = server_mock.get("/validate-dataset?url=" + unexpected_data_url)
#     assert response.status_code == 400
#     assert response.json() == {"detail": "Invalid data format"}


# def test_server_returns_404_error_on_invalid_url(start_mock_server):
#     response = server_mock.get("/validate-dataset?url=" + invalid_url)
#     assert response.status_code == 404
#     assert response.json() == {"detail": "Resource not found"}
