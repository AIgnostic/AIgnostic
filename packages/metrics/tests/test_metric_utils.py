from metrics.utils import (
    _fgsm_attack,
    # _lime_explanation,
    # __query_model
)
import numpy as np
import pytest


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


@pytest.mark.skip("Not implemented yet")
def test_query_model():
    # TODO: Implement this test
    pass
