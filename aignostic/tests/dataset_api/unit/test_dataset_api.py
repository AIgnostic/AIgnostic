# from fastapi.testclient import TestClient
# from threading import Thread
# from typing import List
# import pytest
# from mock_server import app as client_mock
# from aignostic.dataset.validate_dataset_api import app as server_mock
# from tests.dataset_api.constants import expected_ACS_column_names

# server_mock = TestClient(server_mock)
# client_mock = TestClient(client_mock)

# local_server = "http://127.0.0.1:5005"
# valid_url = local_server + "/fetch-datapoints"
# unexpected_data_url = local_server + "/invalid-data"
# invalid_url = local_server + "/invalid-url"


# # Client tests
# def test_client_returns_data():
#     response = client_mock.get("/fetch-datapoints")
#     assert response.status_code == 200
#     assert response.json() != {}


# def test_client_returns_invalid_data_correctly():
#     response = client_mock.get("/invalid-data")
#     assert response.status_code == 200
#     assert not isinstance(response.json()["column_names"], List)


# # Server tests
# @pytest.fixture(scope="module")
# def start_mock_server():
#     def run_mock_server():
#         import uvicorn
#         uvicorn.run(client_mock, host="127.0.0.1", port=5005)

#     thread = Thread(target=run_mock_server)
#     thread.daemon = True
#     thread.start()
#     yield
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
