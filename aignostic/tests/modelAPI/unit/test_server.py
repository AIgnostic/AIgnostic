import pytest
from fastapi.testclient import TestClient
from tests.modelAPI.model.scikit_mock import app as scikit_app
from tests.modelAPI.model.mock import app as mock_app
from pytest_httpserver import HTTPServer
import pandas as pd
from aignostic.pydantic_models.models import DataSet
from folktables import ACSDataSource, ACSEmployment
from sklearn.model_selection import train_test_split
import pickle
import numpy as np
from tests.modelAPI.model.huggingface_binclassifier import app as huggingface_app


client_huggingface = TestClient(huggingface_app)
client_scikit = TestClient(scikit_app)
client_mock = TestClient(mock_app)

def test_non_existent_endpoint_throws_error():
    response = client_scikit.get("/hello")
    print(response)
    assert response.status_code == 404, response.text

def test_mock_api_returns_empty():
    # post empty pandas dataframe
    response = client_mock.post("/predict", json={"columns": {}})
    assert response.status_code == 200, response.text
    assert response.json() == {"columns": {}}, "Empty dataframe not returned given empty input"
    
def test_empty_data_scikit():
    # post empty pandas dataframe
    response = client_scikit.post("/predict", json={"columns": {}})
    assert response.status_code == 200, response.text
    assert response.json() == {"columns": {}}, "Empty dataframe not returned given empty input"


def test_valid_data_huggingface():
    # post a valid text
    response = client_huggingface.post("/predict", json={"text": "I am happy"})
    print(response)
    print(response.json())
    assert response.status_code == 200

