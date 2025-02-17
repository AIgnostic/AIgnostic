from metrics.exceptions import MetricsException
import numpy as np
from metrics.models import CalculateRequest
from sklearn.linear_model import Ridge
from scipy.spatial.distance import euclidean
import requests


def _finite_difference_gradient(
    name: str, features: list[list], model_fn: callable, h: float = 1e-5
) -> np.ndarray:
    """
    Compute the finite difference approximation of the gradient for given data.

    :param name: Name of the metric (for exception handling).
    :param features: datapoints
    :param model_fn: Function that computes the outputs given data (could be a model e.g. pass in query_model)
    :param h: Step size for numerical differentiation.
    :return: Gradient matrix of shape (num_samples, num_features).
    """
    try:
        X = np.array(
            features, dtype=np.float64
        )  # Assuming features are provided in `info`
        num_samples, num_features = X.shape
        gradients = np.zeros_like(X)

        for i in range(num_features):
            X_forward = X.copy()
            X_backward = X.copy()
            X_forward[:, i] += h
            X_backward[:, i] -= h

            # Compute the function values (assuming the metric function is applied row-wise)
            f_forward = np.apply_along_axis(model_fn, 1, X_forward)
            f_backward = np.apply_along_axis(model_fn, 1, X_backward)

            # Compute gradient using central difference
            gradients[:, i] = (f_forward - f_backward) / (2 * h)

        return gradients

    except (TypeError, ValueError, AttributeError, IndexError, ZeroDivisionError) as e:
        raise MetricsException(name, additional_context=str(e))


def _fgsm_attack(x: np.array, gradient: np.array, epsilon: float) -> np.array:
    """
    Compute adversarial example using FGSM.

    Args:
        x: Original input sample (d - dimensional array)
        gradient: Gradient of the loss w.r.t input (d - dimensional array)
        epsilon: Perturbation magnitude

    Returns:
        x_adv: Adversarially perturbed input
    """
    # Generate adversarial example
    x_adv = x + epsilon * np.sign(gradient)
    return x_adv


def _lime_explanation(x: np.ndarray, info: CalculateRequest, num_samples: int = 50,
                      kernel_width: float = 0.75) -> np.ndarray:
    """
    Compute LIME explanation for a black-box model.

    Args:
        x: Input sample (d-dimensional array)
        model: Black-box model (function: R^d -> R)
        num_samples: Number of perturbed samples
        kernel_width: Width of the Gaussian kernel for weighting
    Returns :
        explanation: Linear surrogate model coefficients (d-dimensional array)
    """
    d = x.shape[0]

    # TODO: Update with actual gradients from model
    gradients = np.random.normal(size=(num_samples, d))

    # Generate perturbed samples
    perturbed_samples = _fgsm_attack(x, gradients, epsilon=0.1)

    # TODO: Query model using endpoints rather than arbitrary callable fn
    def model(x):
        return np.sum(x)

    # Compute model predictions for perturbed samples
    predictions = np.array([model(sample) for sample in perturbed_samples])

    # Compute similarity weights using an RBF kernel
    distances = np.array([euclidean(x, sample) for sample in perturbed_samples])
    weights = np.exp(-distances ** 2 / (2 * kernel_width ** 2))

    # Fit a weighted linear regression model
    reg = Ridge(alpha=1.0)
    reg.fit(perturbed_samples - x, predictions, sample_weight=weights)
    return reg.coef_


async def _query_model(inputs: list, info: CalculateRequest):
    """
    Helper function to query the model API

    Params:
    - modelURL : API URL of the model
    - data : Data to be passed to the model in JSON format with DataSet pydantic model type
    - modelAPIKey : API key for the model
    """
    data = inputs

    # Send a POST request to the model API
    if info.model_api_key is None:
        response = requests.post(url=info.model_url, json=data)
    else:
        response = requests.post(
            url=info.model_url,
            json=data,
            headers={"Authorization": f"Bearer {info.model_api_key}"},
        )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise MetricsException(
            detail=e.response.json()["detail"], status_code=e.response.status_code
        )

    _check_model_response(response, data["labels"])

    try:
        # Check if the request was successful

        # Parse the response JSON
        data = response.json()

        # Return the data
        return data
    except Exception as e:
        raise MetricsException(
            detail=f"Could not parse model response - {e}; response = {response.text}"
        )


def _check_model_response(response, labels):
    """
    PRE: response is received from a deserialised pydantic model and labels and types
    have been enforced according to ModelOutput.
    ASSUME: Labels are always correct / have already been validated previously

    Helper function to check the response from the model API and ensure validity compared to data

    Checks are ordered in terms of complexity and computational cost, with the most
    computationally expensive towards the end.

    Params:
    - response : Response object from the model API
    """
    predictions = response.json()["predictions"]
    if len(predictions) != len(labels):
        raise MetricsException(
            additional_context="Number of model outputs does not match expected number of labels",
            status_code=400,
        )

    if len(labels) >= 0:
        if len(predictions[0]) != len(labels[0]):
            raise MetricsException(
                "Number of attributes predicted by model does not match number of target attributes",
                status_code=400,
            )

        for col_index in range(len(labels[0])):
            if not isinstance(predictions[0][col_index], type(labels[0][col_index])):
                raise MetricsException(
                    "Model output type does not match target attribute type",
                    status_code=400,
                )
    """
    TODO: Evaluate if this check is necessary -> O(n) complexity where n is number
    of datapoints.
    (As opposed to O(1) complexity or O(d) complexity for above checks)
    """
    num_attributes = len(labels[0])
    for row in predictions[1:]:
        if len(row) != num_attributes:
            raise MetricsException(
                "Inconsistent number of attributes for each datapoint predicted by model",
                status_code=400,
            )

    """
    TODO: Evaluate if this check is necessary -> O(n*d) complexity where n is number
    of datapoints in batch and d is number of attributes being predicted.
    (As opposed to O(1) complexity or O(d) complexity for above checks)
    """
    for col_index in range(len(predictions[0])):
        col_type = type(labels[0][col_index])
        for row_index in range(len(predictions)):
            if not isinstance(predictions[row_index][col_index], col_type):
                raise MetricsException(
                    "All columns for an output label should be of the same type",
                    status_code=400,
                )
    return
