import numpy as np
from common.utils import nested_list_to_np, np_to_nested_list


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


def test_np_to_nested_list_with_np_array():
    input_value = np.array([[1, 2, 3], [4, 5, 6]])
    expected_output = [[1, 2, 3], [4, 5, 6]]
    result = np_to_nested_list(input_value, "test")
    assert result == expected_output


def test_np_to_nested_list_with_empty_np_array():
    input_value = np.array([])
    expected_output = []
    result = np_to_nested_list(input_value, "test")
    assert result == expected_output


def test_np_to_nested_list_with_none():
    input_value = None
    expected_output = None
    result = np_to_nested_list(input_value, "test")
    assert result == expected_output
