from metrics.utils import (
    _finite_difference_gradient,
    _fgsm_attack,
    _lime_explanation,
    # __query_model
)
import numpy as np
import pytest


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
    const_grad = _finite_difference_gradient("const_fn", sample_data, const_fn)
    assert const_grad.shape == (3, 3)
    assert (const_grad == 0).all()

    # linear function gradient
    linear_grad = _finite_difference_gradient("linear_fn", sample_data, linear_fn)
    assert linear_grad.shape == (3, 3)
    assert np.allclose(linear_grad, 2.0, atol=1e-5)  # Allowing small tolerance

    # quadratic function gradient
    quad_grad = _finite_difference_gradient("quad_fn", sample_data, quad_fn)
    expected_grad = np.array([[2, 4, 6], [8, 10, 12], [14, 16, 18]])
    assert quad_grad.shape == (3, 3)
    assert np.allclose(quad_grad, expected_grad, atol=1e-5)


def test_fgsm_attack():
    x = np.array([1, 2, 3])
    grad = np.array([1, -1, 1])
    epsilon = 0.5
    perturbed_x = np.array([1.5, 1.5, 3.5])
    assert _fgsm_attack(x, grad, epsilon).all() == perturbed_x.all()


@pytest.mark.skip("Not implemented yet")
def test_lime_explanation():
        
    pass


@pytest.mark.skip("Not implemented yet")
def test_query_model():
    # TODO: Implement this test
    pass
