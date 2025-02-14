from metrics.utils import finite_difference_gradient
import numpy as np


def test_finite_difference_gradient_approximation_without_model():
    # constant function
    def const_fn(_):
        return 5

    # linear function
    def linear_fn(x):
        return np.sum(2 * x)

    # quadratic function
    def quad_fn(x):
        return np.sum(x**2)

    sample_data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    # constant function gradient
    const_grad = finite_difference_gradient("const_fn", sample_data, const_fn)
    assert const_grad.shape == (3, 3)
    assert (const_grad == 0).all()

    # linear function gradient
    linear_grad = finite_difference_gradient("linear_fn", sample_data, linear_fn)
    assert linear_grad.shape == (3, 3)
    assert np.allclose(linear_grad, 2.0, atol=1e-5)  # Allowing small tolerance

    # quadratic function gradient
    quad_grad = finite_difference_gradient("quad_fn", sample_data, quad_fn)
    expected_grad = np.array([[2, 4, 6], [8, 10, 12], [14, 16, 18]])
    assert quad_grad.shape == (3, 3)
    assert np.allclose(quad_grad, expected_grad, atol=1e-5)
