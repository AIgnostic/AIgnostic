from mocks.model.gemini_mock import app as gemini_app
from mocks.model.tinystories_1M_mock import app as tinystories_app
from fastapi.testclient import TestClient
import pytest

gemini = TestClient(gemini_app)
tinystories = TestClient(tinystories_app)


@pytest.mark.skip(reason="Skip to enable testing multiple inputs within API limits")
def test_gemini():
    response = gemini.post("/predict", json={
        "features": [["Hello world"]],
        "labels": [[""]],
        "group_ids": []
    })
    assert response.status_code == 200, response.text
    predictions = response.json()["predictions"]
    confidence_scores = response.json()["confidence_scores"]
    assert len(predictions) == 1, f"Expected 1 prediction, got {len(predictions)}"
    assert confidence_scores is None, "Confidence scores should be None"


def test_gemini_multiple_inputs():
    response = gemini.post("/predict", json={
        "features": [
            ["Hello World"],
            ["Who am I? (Max response: 5 words)"],
        ],
        "labels": [
            [""],
            [""],
        ],
        "group_ids": [0, 2]
    })
    assert response.status_code == 200, response.text
    predictions = response.json()["predictions"]
    confidence_scores = response.json()["confidence_scores"]
    assert len(predictions) == 2, f"Expected 2 predictions, got {len(predictions)}"
    assert confidence_scores is None, "Confidence scores should be None"


def test_tinystories_1M_single_input():
    response = tinystories.post("/predict", json={
        "features": [["Humpty dumpty sat"]],
        "labels": [["on the wall"]],
        "group_ids": [0]
    })
    assert response.status_code == 200, response.text
    predictions = response.json()["predictions"]
    confidence_scores = response.json()["confidence_scores"]
    assert len(predictions) == 1, f"Expected 1 prediction, got {len(predictions)}"
    assert confidence_scores is None, "Confidence scores should be None"


def test_tinystories_1M_multiple_inputs():
    response = tinystories.post("/predict", json={
        "features": [
            ["Humpty dumpty sat"],
            ["He huffed and he puffed "],
        ],
        "labels": [
            ["on the wall"],
            ["and he blew the house down"],
        ],
        "group_ids": [0, 1]
    })
    assert response.status_code == 200, response.text
    predictions = response.json()["predictions"]
    confidence_scores = response.json()["confidence_scores"]
    assert len(predictions) == 2, f"Expected 2 predictions, got {len(predictions)}"
    assert confidence_scores is None, "Confidence scores should be None"