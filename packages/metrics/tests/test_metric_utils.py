from metrics.utils import (
    _fgsm_attack,
    _lime_explanation,
    _query_model
)
from metrics.exceptions import ModelQueryException
from metrics.models import CalculateRequest
from common.models import (
    DatasetResponse,
    ModelResponse
)
from unittest.mock import patch, MagicMock
from sklearn.linear_model import Ridge
import numpy as np
import requests
import pytest


def test_fgsm_attack():
    """
    Test perturbations for fgsm attack are correctly computed given gradients, epsilon and input
    """
    x = np.array([1, 2, 3])
    grad = np.array([1, -1, 1])
    epsilon = 0.5
    perturbed_x = np.array([1.5, 1.5, 3.5])
    assert _fgsm_attack(x, grad, epsilon).all() == perturbed_x.all()


"""
    _lime_explanation tests
"""


@pytest.fixture
def mock_info():
    """
    Mock input object for testing
    """
    class MockInfo:
        def __init__(self):
            self.metrics = ["explanation_stability_score"]
            self.input_features = np.array([[1, 2], [3, 4], [5, 6]])
            self.model_url = "http://model-api.com"
            self.model_api_key = "fake_api_key"
            self.regression_flag = False
    return MockInfo()


def mock_query_model(perturbed_samples, info):
    """
    Mock output of querying a model
    """
    class MockResponse:
        def __init__(self):
            self.predictions = np.random.rand(perturbed_samples.shape[0])
            self.confidence_scores = np.random.rand(perturbed_samples.shape[0])
    return MockResponse()


@patch('metrics.utils._query_model', side_effect=mock_query_model)
def test_lime_explanation(mock_query, mock_info):
    kernel_width = 1.5

    # Call the function with the mock data
    coefficients, model = _lime_explanation(mock_info, kernel_width)

    # Check if the returned coefficients are a numpy array
    assert isinstance(coefficients, np.ndarray), "Expected output to be a numpy array"

    # Ensure the coefficients shape matches the number of features
    assert coefficients.shape[0] == mock_info.input_features.shape[1], "Coefficient shape mismatch"

    # Ensure the model is of type Ridge
    assert isinstance(model, Ridge), "Expected the regression model to be of type Ridge"


"""
    _query_model tests
"""


@pytest.fixture(scope='function')
def mock_post():
    with patch('requests.post') as mock:
        yield mock


def test_query_model_success(mock_post):
    """
    Test the _query_model successfully retrieves predictions and confidence scores given valid model
    inputs.
    """
    # Arrange
    generated_input_features = np.array([[1, 2, 3], [4, 5, 6]])
    info = CalculateRequest(
        batch_size=1,
        total_sample_size=10,
        metrics=[],
        model_url="http://fakeurl.com"
    )

    predictions = [[0], [1]]
    confidence_scores = [[0.5], [0.6]]

    # Mock the response object
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "predictions": predictions,
        "confidence_scores": confidence_scores
    }
    mock_post.return_value = mock_response

    # Act
    response = _query_model(generated_input_features, info)

    # Assert
    mock_post.assert_called_once_with(
        url=info.model_url,
        json=DatasetResponse(
            features=generated_input_features.tolist(),
            labels=np.zeros((len(generated_input_features), 1)).tolist(),
            group_ids=np.zeros(len(generated_input_features), dtype=int).tolist(),
        ).model_dump(mode="json")
    )
    assert isinstance(response, ModelResponse)
    assert response.predictions == predictions
    assert response.confidence_scores == confidence_scores


def test_query_model_returns_http_error(mock_post):
    """
    Assert a ModelQueryException is raised when the model API returns an HTTP error.
    """
    # Arrange
    generated_input_features = np.array([[1, 2, 3], [4, 5, 6]])
    info = CalculateRequest(
        batch_size=1,
        total_sample_size=10,
        metrics=[],
        model_url="http://fakeurl.com"
    )

    # Mock the response object to simulate an HTTP 404 error
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=MagicMock(status_code=404, json=lambda: {"detail": "Not Found"})
    )
    mock_post.return_value = mock_response

    # Act & Assert
    with pytest.raises(ModelQueryException):
        _query_model(generated_input_features, info)
