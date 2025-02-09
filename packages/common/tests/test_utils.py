import pytest
import numpy as np
from common.utils import nested_list_to_np

# FILE: packages/common/tests/test_utils.py


def test_nested_list_to_np_with_nested_list():
    input_value = [[1, 2, 3], [4, 5, 6]]
    expected_output = np.array([[1, 2, 3], [4, 5, 6]])
    result = nested_list_to_np(input_value)
    assert np.array_equal(result, expected_output)


def test_nested_list_to_np_with_empty_list():
    input_value = []
    expected_output = []
    result = nested_list_to_np(input_value)
    assert result == expected_output


def test_nested_list_to_np_with_none():
    input_value = None
    expected_output = None
    result = nested_list_to_np(input_value)
    assert result == expected_output
