import pytest
from fastapi.testclient import TestClient
from tests.modelAPI.model.scikit_mock import app as scikit_app
from tests.modelAPI.model.mock import app as mock_app
from pytest_httpserver import HTTPServer
import pandas as pd
from aignostic.pydantic_models.models import DataSet

client_scikit = TestClient(scikit_app)
client_mock = TestClient(mock_app)

def test_server():
    response = client_scikit.get("/hello")
    print(response)
    assert response.status_code == 200, response.text
    assert response.text == '"Hello World"'

def test_empty_data_mock():
    # post empty pandas dataframe
    response = client_mock.post("/predict", json={"columns": {}})
    assert response.status_code == 200, response.text
    assert response.json() == {"columns": {}}, "Empty dataframe not returned given empty input"
    
def test_empty_data_scikit():
    pass

def test_nothing():
    pass