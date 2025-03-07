from fastapi.testclient import TestClient
from mocks.api_utils import MOCK_MODEL_API_KEY
from mocks.model.huggingface_binclassifier import app as huggingface_app
from mocks.model.scikit_mock_classifier import app as scikit_app
from mocks.model.finbert import app as finbert_app
from mocks.model.mock import app as mock_app
from folktables import ACSDataSource, ACSEmployment
import pandas as pd
import pytest
from mocks.utils import load_scikit_model

# TODO: Modify the tests to use pydantic models to ensure they are correctly validated

huggingface_mock = TestClient(huggingface_app)
scikit_mock = TestClient(scikit_app)
basic_mock = TestClient(mock_app)
finbert_mock = TestClient(finbert_app)


def test_non_existent_endpoint_throws_error():
    response = scikit_mock.get("/hello")
    assert response.status_code == 404, response.text


def test_scikit_read_root():
    response = scikit_mock.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Scikit-Learn Model API"}


def test_finbert_read_root():
    response = finbert_mock.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FinBERT Model API"}


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
    model = model = load_scikit_model('scikit_model.sav')
    y_hat = model.predict(features)

    assert response.json()["predictions"] == [y_hat.tolist()], (
        "Model output does not match expected output"
    )
    assert len(response.json()["confidence_scores"]) == len(y_hat), (
        "Confidence scores do not match the number of predictions"
    )
    for scores in response.json()["confidence_scores"]:
        assert all([0 <= score <= 1 for score in scores]), (
            "Confidence scores are not probabilities"
        )


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
        "confidence_scores": []
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
    print(response.json())
    predictions = response.json()["predictions"]
    confidence_scores = response.json()["confidence_scores"]
    assert len(predictions) == 1, f"Expected 1 prediction, got {len(predictions)}"
    assert len(confidence_scores) == 1, f"Expected 1 confidence score, got {len(confidence_scores)}"
    assert predictions[0][0] == "neutral", "Single data output is not the expected value"
    print(confidence_scores)
    assert confidence_scores[0][0] <= 1, "Probability score is greater than 1"
    assert confidence_scores[0][0] >= 0, "Probability score is less than 0"


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
    assert len(response.json()["confidence_scores"]) == 3, "Incorrect number of confidence scores produced"
    assert response.json()["predictions"][0][0] == "negative", "First input not classified as negative"
    assert response.json()["predictions"][1][0] == "positive", "Second input not classified as positive"
    assert response.json()["predictions"][2][0] == "neutral", "Third input not classified as neutral"


def test_probabilities_sum_to_one():
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
    for confidence_scores in response.json()["confidence_scores"]:
        assert confidence_scores[0] <= 1, "Probability score is greater than 1"
        assert confidence_scores[0] >= 0, "Probability score is less than 0"
        assert sum(confidence_scores) == pytest.approx(1), "Confidence scores do not sum to 1"
