from fastapi.testclient import TestClient
from tests.modelAPI.model.scikit_mock import app as scikit_app
from tests.modelAPI.model.mock import app as mock_app
import pandas as pd
from folktables import ACSDataSource, ACSEmployment
import pickle
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
    response = client_mock.post("/predict", json={
        "column_names": [],  # Empty list for no columns
        "rows": [[]]  # Empty list for no rows
    })
    assert response.status_code == 200, response.text
    assert response.json() == {"column_names": [], "rows": [[]]}, "Empty values not returned given empty input"


def test_empty_data_scikit():
    # post empty pandas dataframe
    response = client_mock.post("/predict", json={
        "column_names": [],  # Empty list for no columns
        "rows": [[]]  # Empty list for no rows
    })
    assert response.status_code == 200, response.text
    assert response.json() == {"column_names": [], "rows": [[]]}, "Empty values not returned given empty input"


def test_valid_data_scikit_folktables():
    # Import the folktables dataset and load the employment data
    data_source: ACSDataSource = ACSDataSource(survey_year='2018', horizon='1-Year', survey='person')
    acs_data: pd.DataFrame = data_source.get_data(states=[
        "AL"
    ], download=True)[0:1]
    features, _, _ = ACSEmployment.df_to_numpy(acs_data)

    # Test the response is not empty given a non-empty input
    response = client_scikit.post("/predict", json={"column_names": None, "rows": features.tolist()})
    assert response.status_code == 200, response.text

    # Test the response is the same as the expected response from the pickled model
    model = pickle.load(open('scikit_model.sav', 'rb'))
    y_hat = model.predict(features)

    assert response.json() == {
        "column_names": None,
        "rows": [y_hat.tolist()]
    }, "Model output does not match expected output"


def test_valid_data_huggingface_empty():
    # post a valid text
    response = client_huggingface.post("/predict", json={"column_names": [], "rows": [["Hello world"]]})
    with open('output.txt', 'w') as f:
        f.write(response.text)
    assert response.status_code == 200


def test_invalid_inputs_fail():
    """
    Test that invalid inputs fail when /predict is called
    """
    input = {"column_names": [], "rows": ["Hello world", "Hello world"]}
    response = client_huggingface.post("/predict", json=input)
    assert response.status_code == 422, response.text


def test_multiple_inputs():
    """
    Test that multiple inputs are accepted and processed correctly by the pydantic model and 
    the HuggingFace model API
    """
    input = {"column_names": [], "rows": [["Hello world"], ["Hello world"], ["Pizza is unhealthy"]]}
    response = client_huggingface.post("/predict", json=input)
    assert response.status_code == 200, response.text
    out = response.json()
    assert len(out["column_names"]) == 1, "Multiple inputs not processed correctly"
    assert len(out["rows"]) == 3, "Multiple inputs not processed correctly"
    