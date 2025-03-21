from worker.worker import WorkerException, Worker
import pytest
from unittest.mock import MagicMock

worker = Worker()


def generate_mock_response(json_data: dict):
    """
    Test helper function to generate a mock response object
    """
    response = MagicMock()
    response.json.return_value = json_data
    return response


def test_incorrect_number_of_outputs_raises_400():
    predictions = [[0], [1], [0], [1], [1], [0]]
    with pytest.raises(WorkerException) as e:
        worker._check_model_response(predictions, [[0], [1], [0], [1], [0], [1], [1], [0]])
    assert e.value.status_code == 400
    assert (
        "Number of model outputs does not match expected number of labels"
        in e.value.detail
    )


def test_incorrect_number_of_output_attributes_raises_400():
    predictions = [[0, 1], [1, 0], [0, 1], [1, 0], [1, 0], [0, 1]]
    with pytest.raises(WorkerException) as e:
        worker._check_model_response(predictions, [[0], [1], [0], [1], [0], [1]])
    assert e.value.status_code == 400
    assert (
        "Number of attributes predicted by model does not match number of target attributes"
        in e.value.detail
    )


def test_incorrect_output_type_raises_400():
    predictions = [[0], [1], [0], [1], [1], [0]]
    with pytest.raises(WorkerException) as e:
        worker._check_model_response(predictions, [["0"], ["1"], ["0"], ["1"], ["0"], ["1"]])
    assert e.value.status_code == 400
    assert "Model output type does not match target attribute type" in e.value.detail


def test_incorrect_numeric_types_raises_400():
    predictions = [[0], [1], [0], [1], [1], [0]]
    with pytest.raises(WorkerException) as e:
        worker._check_model_response(predictions, [[0.4], [1.3], [0.2], [1.0], [1.0], [0.1]])
    assert e.value.status_code == 400
    assert "Model output type does not match target attribute type" in e.value.detail


def test_correct_output_passes_ints():
    predictions = [[0], [1], [0], [1], [1], [0]]
    worker._check_model_response(predictions, [[0], [1], [0], [1], [1], [0]])


def test_correct_output_passes_strs():
    predictions = [["0"], ["1"], ["0"], ["1"], ["1"], ["0"]]
    worker._check_model_response(predictions, [["0"], ["1"], ["0"], ["1"], ["1"], ["0"]])


def test_inconsistent_output_length_mismatch():
    predictions = [[0], [1], [0], [1], [1], [0, 1]]
    with pytest.raises(WorkerException) as e:
        worker._check_model_response(predictions, [[0], [1], [0], [1], [1], [0]])
    assert e.value.status_code == 400
    assert (
        "Inconsistent number of attributes for each datapoint predicted by model"
        in e.value.detail
    )


def test_inconsistent_output_type_mismatch():
    predictions = [[0], ["1"], [0], [1], [1], [0]]
    with pytest.raises(WorkerException) as e:
        worker._check_model_response(predictions, [[0], [1], [0], [1], [1], [0]])
    assert e.value.status_code == 400
    assert (
        "All columns for an output label should be of the same type" in e.value.detail
    )
