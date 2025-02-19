from metrics.utils import (
    _fgsm_attack,
    # _lime_explanation,
    _query_model
)
from metrics.models import CalculateRequest
from common.models import (
    ModelInput,
    ModelResponse
)
import numpy as np
from unittest.mock import patch, MagicMock
import pytest
import requests
from metrics.exceptions import ModelQueryException


def test_fgsm_attack():
    x = np.array([1, 2, 3])
    grad = np.array([1, -1, 1])
    epsilon = 0.5
    perturbed_x = np.array([1.5, 1.5, 3.5])
    assert _fgsm_attack(x, grad, epsilon).all() == perturbed_x.all()


@pytest.mark.skip("Not implemented yet")
def test_lime_explanation():
    # TODO: Implement this test
    pass


@pytest.fixture
def mock_post():
    with patch('requests.post') as mock:
        yield mock


def test_query_model_success(mock_post):
    # Arrange
    generated_input_features = np.array([[1, 2, 3], [4, 5, 6]])
    info = CalculateRequest(metrics=[], model_url="http://fakeurl.com")

    # Mock the response object
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "predictions": [[0], [1]],
        "confidence_scores": [[0.5], [0.6]]
    }
    mock_post.return_value = mock_response

    # Act
    response = _query_model(generated_input_features, info)

    # Assert
    mock_post.assert_called_once_with(
        url=info.model_url,
        json=ModelInput(
            features=generated_input_features.tolist(),
            labels=np.zeros((len(generated_input_features), 1)).tolist(),
            group_ids=np.zeros(len(generated_input_features), dtype=int).tolist(),
        ).model_dump(mode="json")
    )
    assert isinstance(response, ModelResponse)


def test_query_model_http_error(mock_post):
    # Arrange
    generated_input_features = np.array([[1, 2, 3], [4, 5, 6]])
    info = CalculateRequest(metrics=[], model_url="http://fakeurl.com")

    # Mock the response object to simulate an HTTP 404 error
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=MagicMock(status_code=404, json=lambda: {"detail": "Not Found"})
    )
    mock_post.return_value = mock_response

    # Act & Assert
    with pytest.raises(ModelQueryException):
        _query_model(generated_input_features, info)
