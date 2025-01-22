import aignostic.pydantic_models.models as models
import numpy as np
from tests.modelAPI.model.mock import app as mock_app
from fastapi.testclient import TestClient
import pandas as pd

mock_app = TestClient(mock_app)


def test_conversion_from_numpy():
    """
    Test conversion from numpy array to pydantic model
    """
    arr = np.array([[1, 2, 3], [4, 5, 6]]).astype(float)
    data = models.arr_to_JSON(arr)
    response = mock_app.post("/predict", json=data)
    assert response.status_code == 200, response.text


def test_conversion_from_pandas():
    """
    Test conversion from pandas dataframe to pydantic model
    """
    df = np.array([[1, 2, 3], [4, 5, 6]]).astype(float)
    df = pd.DataFrame(df, columns=["a", "b", "c"])
    data = models.df_to_JSON(df)
    response = mock_app.post("/predict", json=data)
    assert response.status_code == 200, response.text


def test_conversion_from_csv():
    """
    Test conversion from csv to pydantic model
    """
    data = models.csv_to_JSON("tests/modelAPI/unit/csv_testfile.csv")
    response = mock_app.post("/predict", json=data)
    assert response.status_code == 200, response.text
