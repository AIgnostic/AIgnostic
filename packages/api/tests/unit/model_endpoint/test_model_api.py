from fastapi.testclient import TestClient
from tests.utils.api_utils import MOCK_MODEL_API_KEY
from tests.utils.model.huggingface_binclassifier import app as huggingface_app
from tests.utils.model.scikit_mock import app as scikit_app
from tests.utils.model.finbert import app as finbert_app
from tests.utils.model.mock import app as mock_app
from folktables import ACSDataSource, ACSEmployment
import pandas as pd
import pickle
import pytest

huggingface_mock = TestClient(huggingface_app)
scikit_mock = TestClient(scikit_app)
basic_mock = TestClient(mock_app)
finbert_mock = TestClient(finbert_app)


def test_non_existent_endpoint_throws_error():
    response = scikit_mock.get("/hello")
    assert response.status_code == 404, response.text


def test_mock_returns_empty():
    # post empty pandas dataframe
    response = basic_mock.post("/predict", json={
        "features": [],  # Empty list for no columns
        "labels": [],  # Empty list for no rows
        "group_ids": []  # Empty list for no group IDs
    })
    assert response.status_code == 200, response.text
    assert response.json() == {
        "predictions": [],
        "confidence_scores": None
    }, "Empty values not returned given empty input"


def test_empty_data_scikit():
    response = scikit_mock.post("/predict", json={
        "features": [],  # Empty list for no columns
        "labels": [],  # Empty list for no rows
        "group_ids": []  # Empty list for no group IDs
    }, headers={"Authorization": f"Bearer {MOCK_MODEL_API_KEY}"})
    assert response.status_code == 200, response.text
    assert response.json() == {
        "predictions": [],
        "confidence_scores": None
    }, "Empty values not returned given empty input"


@pytest.mark.skip(reason="Test to be implemented")
def test_singleton_data_scikit():
    pass


def test_valid_data_scikit_folktables():
    # Import the folktables dataset and load the employment data
    data_source: ACSDataSource = ACSDataSource(survey_year='2018', horizon='1-Year', survey='person')
    acs_data: pd.DataFrame = data_source.get_data(states=[
        "AL"
    ], download=True)[0:1]
    features, labels, groups = ACSEmployment.df_to_numpy(acs_data)

    # Test the response is not empty given a non-empty input
    response = scikit_mock.post(
        "/predict",
        json={
            "features": features.tolist(),
            "labels": [labels.tolist()],
            "group_ids": groups.tolist()
        },
        headers={"Authorization": f"Bearer {MOCK_MODEL_API_KEY}"}
    )
    assert response.status_code == 200, response.text

    # Test the response is the same as the expected response from the pickled model
    model = pickle.load(open('scikit_model.sav', 'rb'))
    y_hat = model.predict(features)

    assert response.json() == {
        "predictions": [y_hat.tolist()],
        "confidence_scores": None
    }, "Model output does not match expected output"


def test_valid_data_huggingface():
    # post a valid text
    response = huggingface_mock.post("/predict", json={
        "features": [["Hello World"]],
        "labels": [["Positive"]],
        "group_ids": []})
    assert response.status_code == 200


def test_invalid_inputs_fail_hf_binclassifier():
    """
    Test that invalid inputs fail when /predict is called
    """
    input = {"features": ["Hello world", "Hello world"], "labels": [["Positive", "Positive"]], "group_ids": []}
    response = huggingface_mock.post("/predict", json=input)
    assert response.status_code == 422, response.text


def test_multiple_inputs_hf_binclassifier():
    """
    Test that multiple inputs are accepted and processed correctly by the pydantic model and
    the HuggingFace model API
    """
    input = {"features": [["Hello world"], ["Hello world"], ["Pizza is unhealthy"]],
             "labels": [["Positive"], ["Positive"], ["Positive"]],
             "group_ids": [1, 2, 3]
             }
    response = huggingface_mock.post("/predict", json=input)
    assert response.status_code == 200, response.text
    out = response.json()
    assert len(out["predictions"]) == 3, "Multiple inputs not processed correctly"


def test_empty_input_finbert():
    response = finbert_mock.post("/predict", json={
        "features": [],  # Empty list for no columns
        "labels": [],  # Empty list for no rows
        "group_ids": []  # Empty list for no group IDs
    })
    assert response.status_code == 200, response.text
    assert response.json() == {
        "predictions": [],
        "confidence_scores": None
    }, "Empty values not returned given empty input"


def test_invalid_input_finbert():
    response = finbert_mock.post("/predict", json={
        "features": ["Hello world", "Hello world"],
        "labels": ["Positive", "Positive"],
        "group_ids": []
    })
    assert response.status_code == 422, response.text


def test_finbert_single_input():
    response = finbert_mock.post("/predict", json={
        "features": [["Hello world"]],
        "labels": [["neutral"]],
        "group_ids": []
    })
    assert response.status_code == 200, response.text
    assert response.json()["predictions"][0][0]["label"] == "neutral", "Single data output is not the expected value"


def test_finbert_multiple_inputs():
    response = finbert_mock.post("/predict", json={
        "features": [
            ["Tech stocks are bearish with investors fearing a burst in the AI bubble"],
            ["The stock market is bullish with investors optimistic about the future"],
            ["The market will be the same tomorrow as it was the same yesterday"]
        ],
        "labels": [
            ["negative"],
            ["positive"],
            ["neutral"]
        ],
        "group_ids": []
    })
    assert response.status_code == 200, response.text
    assert len(response.json()["predictions"]) == 3, "Incorrect number of outputs produced given number of inputs"
    assert response.json()["predictions"][0][0]["label"] == "negative", "First input not classified as negative"
    assert response.json()["predictions"][1][0]["label"] == "positive", "Second input not classified as positive"
    assert response.json()["predictions"][2][0]["label"] == "neutral", "Third input not classified as neutral"
