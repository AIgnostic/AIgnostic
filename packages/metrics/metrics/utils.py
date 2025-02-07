import numpy as np
from api.metrics.metrics import MetricsException


def finite_difference_gradient(name: str, features: list[list], model_fn: callable, h: float = 1e-5) -> np.ndarray:
    """
    Compute the finite difference approximation of the gradient for given data.

    :param name: Name of the metric (for exception handling).
    :param features: datapoints
    :param model_fn: Function that computes the outputs given data (could be a model e.g. pass in query_model)
    :param h: Step size for numerical differentiation.
    :return: Gradient matrix of shape (num_samples, num_features).
    """
    try:
        X = np.array(features, dtype=np.float64)  # Assuming features are provided in `info`
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
