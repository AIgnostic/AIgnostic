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

def test_valid_data_scikit_folktables():
    pass
    # # Import the folktables dataset and load the employment data 
    # data_source : ACSDataSource = ACSDataSource(survey_year='2018', horizon='1-Year', survey='person')
    # acs_data : pd.DataFrame = data_source.get_data(states=[
    #     "AL"
    # ], download=True)[0:1]

    # features : np.ndarray
    # label : np.ndarray
    # features, label, _ = ACSEmployment.df_to_numpy(acs_data)

    # # Test the response is not empty given a non-empty input
    # response = client_scikit.post("/predict", json={features.})
    # assert response.status_code == 200, response.text

    # # Test the response is the same as the expected response from the pickled model
    # model = pickle.load(open('scikit_model.sav', 'rb'))
    # y_hat = model.predict(features)
