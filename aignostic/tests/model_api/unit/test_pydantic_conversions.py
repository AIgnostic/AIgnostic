import aignostic.pydantic_models.data_models as data_models
import numpy as np
from tests.model_api.model.mock import app as mock_app
from fastapi.testclient import TestClient
import pandas as pd

mock_client: TestClient = TestClient(mock_app)


def test_conversion_from_numpy():
    """
    Test conversion from numpy array to pydantic model
    """
    arr = np.array([[1, 2, 3], [4, 5, 6]]).astype(float)
    data = data_models.arr_to_JSON(arr)
    data["column_names"] = ["a", "b", "c"]
    response = mock_client.post("/predict", json=data)
    assert response.status_code == 200, response.text


def test_conversion_from_pandas():
    """
    Test conversion from pandas dataframe to pydantic model
    """
    df = np.array([[1, 2, 3], [4, 5, 6]]).astype(float)
    df = pd.DataFrame(df, columns=["a", "b", "c"])
    data = data_models.df_to_JSON(df)
    response = mock_client.post("/predict", json=data)
    assert response.status_code == 200, response.text


def test_conversion_from_csv():
    """
    Test conversion from csv to pydantic model
    """
    data = data_models.csv_to_JSON("tests/model_api/unit/csv_testfile.csv")
    response = mock_client.post("/predict", json=data)
    assert response.status_code == 200, response.text
