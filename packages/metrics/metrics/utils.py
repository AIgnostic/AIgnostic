from typing import Optional
from metrics.exceptions import MetricsException, ModelQueryException
import numpy as np
from metrics.models import CalculateRequest
from pydantic import HttpUrl
from sklearn.linear_model import Ridge
from scipy.spatial.distance import euclidean
import requests
from common.models import ModelInput, ModelResponse


def _finite_difference_gradient(
    name, features: list[list], model_fn: callable, h: float = 1e-5
) -> np.ndarray:
    """
    Compute the finite difference approximation of the gradient for given data.

    Args:
        name: Name of the metric (for exception handling).
        features: List of data points (2D list).
        model_fn: Function that computes the outputs given data (could be a model).
        h: Step size for numerical differentiation (default is 1e-5).

    Returns:
        Gradient matrix of shape (num_samples, num_features).
    """
    try:
        X = np.array(features, dtype=np.float64)
        num_samples, num_features = X.shape
        gradients = np.zeros_like(X)

        for i in range(num_features):
            X_forward = X.copy()
            X_backward = X.copy()
            X_forward[:, i] += h
            X_backward[:, i] -= h

            # TODO: Update with actual model API endpoint call

            # Compute the function values (assuming the metric function is applied row-wise)
            f_forward = np.apply_along_axis(model_fn, 1, X_forward)
            f_backward = np.apply_along_axis(model_fn, 1, X_backward)

            # Compute gradient using central difference
            gradients[:, i] = (f_forward - f_backward) / (2 * h)

        return gradients

    except (TypeError, ValueError, AttributeError, IndexError, ZeroDivisionError) as e:
        raise MetricsException(name, detail=str(e))


def _fgsm_attack(x: np.array, gradient: np.array, epsilon: float) -> np.array:
    """
    Compute adversarial example using FGSM.

    Args:
        x: Original input sample (d-dimensional array)
        gradient: Gradient of the loss w.r.t. input (d-dimensional array)
        epsilon: Perturbation magnitude

    Returns:
        x_adv: Adversarially perturbed input
    """
    # Generate adversarial example
    x_adv = x + epsilon * np.sign(gradient)
    return x_adv


async def _lime_explanation(info: CalculateRequest, kernel_width: float = 0.75) -> np.ndarray:
    """
    Compute LIME explanation for a black-box model.

    Args:
        info: information required to compute the explanation including input_features,
            model_url and model_api_key
        kernel_width: Width of the Gaussian kernel for weighting

    Returns :
        explanation: Linear surrogate model coefficients (d-dimensional array)
    """
    num_samples, d = info.input_features.shape[0]

    # TODO: Update with actual gradients once implemented
    gradients = np.random.normal(size=(num_samples, d))

    # Generate perturbed samples
    perturbed_samples = _fgsm_attack(info.input_features, gradients, epsilon=0.1)

    # Construct dictionary for model input (labels and group_ids are not required)
    n = len(perturbed_samples)
    model_input = ModelInput(
        features=perturbed_samples.tolist(),
        labels=np.zeros(n).tolist(),
        group_ids=np.zeros(n).tolist(),
    )

    # Call model endpoint to get confidence scores
    response: ModelResponse = await _query_model(model_input, info.model_url, info.model_api_key)

    # Compute model predictions for perturbed samples
    predictions = response.predictions

    if predictions is None:
        raise ModelQueryException(
            detail="Model response does not contain predictions",
            status_code=400
        )

    # Compute similarity weights using an RBF kernel
    distances = np.array([euclidean(info.input_features, sample) for sample in perturbed_samples])
    weights = np.exp(-distances ** 2 / (2 * kernel_width ** 2))

    # Fit a weighted linear regression model
    reg_model = Ridge(alpha=1.0)
    reg_model.fit(perturbed_samples - info.input_features, predictions, sample_weight=weights)
    return reg_model.coef_, reg_model


async def _query_model(data: dict, model_url: HttpUrl,
                        model_api_key: Optional[str] = None) -> dict:
    """
    Helper function to query the model API

    Params:
    - data : Data to be sent to the model
    - modelURL : API URL of the model
    - modelAPIKey : API key for the model

    Returns:
    - dict : Response from the model API
    """
    if model_api_key is None:
        response = requests.post(url=model_url, json=data)
    else:
        response = requests.post(
            url=model_url,
            json=data,
            headers={"Authorization": f"Bearer {model_api_key}"},
        )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise ModelQueryException(
            detail=e.response.json()["detail"],
            status_code=e.response.status_code
        )

    try:
        return response.json()
    except Exception as e:
        raise ModelQueryException(
            detail=str(e),
            status_code=500
        )
