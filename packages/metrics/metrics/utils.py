from metrics.exceptions import ModelQueryException
from metrics.models import CalculateRequest
from common.models import DatasetResponse, ModelResponse
from sklearn.linear_model import Ridge
from scipy.spatial.distance import euclidean
import numpy as np
import requests

# TODO: Update pydocs for regression tasks


def _finite_difference_gradient_predictions(
    info: CalculateRequest,
    h: float = 1e-5
) -> np.ndarray:
    """
    Compute the finite difference approximation of the gradient for given data.

    Args:
        info: Information required to compute the gradient including info.input_features,
              model_url and model_api_key.
        h: Perturbation magnitude.

    Returns:
        Gradient matrix of shape (num_samples, num_features).
    """
    X = np.array(info.input_features, dtype=np.float64)
    _, num_features = X.shape
    gradients = np.zeros_like(X)

    for i in range(num_features):
        X_forward = X.copy()
        X_backward = X.copy()
        X_forward[:, i] += h
        X_backward[:, i] -= h

        forward_out = np.array(_query_model(X_forward, info).predictions)
        assert forward_out.shape == (len(X), 1), f"Forward output shape is {forward_out.shape}"

        backward_out = np.array(_query_model(X_backward, info).predictions)
        assert backward_out.shape == (len(X), 1), f"Backward output shape is {backward_out.shape}"

        forward_out = forward_out.reshape(-1)
        backward_out = backward_out.reshape(-1)

        # Compute gradient using central difference
        gradients[:, i] = (forward_out - backward_out) / (2 * h)

    return gradients


def _finite_difference_gradient_confidence_scores(
    info: CalculateRequest,
    h: float = 1e-5
) -> np.ndarray:
    """
    Compute the finite difference approximation of the gradient for given data. Use the
    confidence scores for the predicted class instead of the predictions.

    :param info: Information required to compute the gradient including info.input_features,
                 info.confidence_scores, model_url and model_api_key.
    """
    X = np.array(info.input_features, dtype=np.float64)
    num_datapoints, num_columns = X.shape
    gradients = np.zeros_like(X)
    print("Calculating finite difference gradient for confidence scores")
    print(f"Info: {info}")
    for j in range(num_columns):
        X_forward = X.copy()
        X_backward = X.copy()
        X_forward[:, j] += h
        X_backward[:, j] -= h

        print("reached calculation of target class indices")
        # target_class_indices should be a 2D array with shape (num_samples,)
        # It represents the index of the predicted class for each sample
        target_class_indices = np.argmax(info.confidence_scores, axis=1)

        forward_out = np.array(_query_model(X_forward, info).confidence_scores)
        backward_out = np.array(_query_model(X_backward, info).confidence_scores)

        # for each datapoint, get the confidence score of the target class
        column_forward = forward_out[np.arange(num_datapoints), target_class_indices]
        column_backward = backward_out[np.arange(num_datapoints), target_class_indices]

        gradients[:, j] = (column_forward - column_backward) / (2 * h)
    print("returning gradients")
    return gradients


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


# TODO: Refactor ESP flag to cleaner alternative (modified to make ESP pass)
def _lime_explanation(info: CalculateRequest, kernel_width: float = 0.75, esp=False) -> np.ndarray:
    """
    Compute LIME explanation for a black-box model.

    Args:
        info: information required to compute the explanation including info.input_features,
            confidence_scores, model_url and model_api_key
        kernel_width: Width of the Gaussian kernel for weighting
        esp: flag indicating if the metric to compute is Explainability Sparsity Score (ESP always
            uses predictions - not probabilities) # TODO: Check if ESP really does always use predictions

    Returns:
        explanation: Linear surrogate model coefficients (d-dimensional array)
    """
    num_samples, d = info.input_features.shape

    # TODO: Change to probabilities instead of probabilities
    # Need total softmax as we can identify if the class value changes
    #  e.g. 0.9 -> 0.1 means some other class higher p value

    # Binary -> Bernoulli Noise
    # Assume numeric values for now
    # TODO: Add support for categorical features
    perturbed_samples = info.input_features + np.random.normal(
        scale=0.1 * np.std(info.input_features, axis=0),
        size=(num_samples, d)
    )

    # Call model endpoint to get confidence scores
    response: ModelResponse = _query_model(perturbed_samples, info)
    # Compute model probabilities for perturbed samples
    # TODO: Remove ESP param for alternatives
    outputs = response.predictions if (info.regression_flag or esp) else response.confidence_scores

    if outputs is None:
        raise ModelQueryException(
            detail="Model response does not contain probability scores for outputs",
            status_code=400
        )

    if not info.regression_flag:
        outputs = np.clip(outputs, 0, 1)

    # Compute similarity weights using an RBF kernel
    distances = np.array([euclidean(info.input_features[i], sample) for i, sample in enumerate(perturbed_samples)])

    epsilon = 1e-10     # Small constant for numerical stability (avoid division by zero)
    weights = np.exp(-distances ** 2 / (2 * kernel_width ** 2)) + epsilon

    # Fit a weighted linear regression model
    reg_model = Ridge(alpha=1.0)
    reg_model.fit(perturbed_samples - info.input_features, outputs, sample_weight=weights)
    return reg_model.coef_, reg_model


def _query_model(generated_input_features: np.array, info: CalculateRequest) -> ModelResponse:
    """
    Helper function to query the model API using the generated input features,
    not the input features from the CalculateRequest object.

    Params:
    - generated_input : Input data to be sent to the model API
    - info : Information required to query the model API

    Returns:
    - response : Response from the model API
    """

    model_input = DatasetResponse(
        features=generated_input_features.tolist(),
        labels=np.zeros((len(generated_input_features), 1)).tolist(),
        group_ids=np.zeros(len(generated_input_features), dtype=int).tolist(),
    )

    if info.model_api_key is None:
        response = requests.post(url=info.model_url, json=model_input.model_dump(mode="json"))
    else:

        print(f"info.model_url = {info.model_url}")
        response = requests.post(
            url=info.model_url,
            json=model_input.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {info.model_api_key}"},
        )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise ModelQueryException(
            detail=e.response.json()["detail"],
            status_code=e.response.status_code
        )

    try:
        return ModelResponse(**response.json())
    except Exception as e:
        raise ModelQueryException(
            detail=str(e),
            status_code=500
        )
