from metrics.metrics import MetricsException
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

    
def _lime_explanation (x: np.ndarray, info: CalculateRequest, num_samples: int = 50,
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
    model = lambda x: np.sum(x)

    # Compute model predictions for perturbed samples
    predictions = np.array([model(sample) for sample in perturbed_samples])
    
    # Compute similarity weights using an RBF kernel
    distances = np.array([euclidean(x, sample) for sample in perturbed_samples])
    weights = np.exp(-distances **2 / (2 * kernel_width **2))

    # Fit a weighted linear regression model
    reg = Ridge(alpha=1.0)
    reg.fit(perturbed_samples - x, predictions, sample_weight=weights)
    return reg.coef_
