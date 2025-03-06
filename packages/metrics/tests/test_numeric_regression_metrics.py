from metrics.models import CalculateRequest, MetricValue
import pytest
from tests.server_factory import (
    server_factory,
    HOST,
    server_configs
)
from metrics.metrics import calculate_metrics
from tests.metric_mocks.mock_regressor_num_input import (
    TEST_DATA_REGRESSION
)

server_factory = server_factory  # To suppress lint errors

# Mock name used to access server_config fields
mock_name = "numeric_regression"


@pytest.fixture(scope="module")
def apply_server_factory(server_factory):
    with server_factory(mock_name):
        yield


def test_high_stability_ntg(apply_server_factory):
    metric_name = "explanation_stability_score"
    print("reached 3rd test")
    hs_info = CalculateRequest(
        batch_size=10,
        total_sample_size=10,
        metrics=[metric_name],
        task_name="regression",
        input_features=TEST_DATA_REGRESSION.features,
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict-perfect-stability",
        model_api_key="None",
        true_labels=TEST_DATA_REGRESSION.labels,
        predicted_labels=TEST_DATA_REGRESSION.labels,
        # TODO: Update metrics library to only require confidence score based on metric, task_name combination
        confidence_scores=[[1]] * len(TEST_DATA_REGRESSION.labels),
        # TODO: Remove and update with task_name instead
        regression_flag=True
    )

    hs_result = calculate_metrics(hs_info)

    assert isinstance(hs_result.metric_values[metric_name], MetricValue), hs_result

    assert hs_result.metric_values[metric_name].computed_value == pytest.approx(1.0), hs_result


def test_low_stability_ntg(apply_server_factory):
    metric_name = "explanation_stability_score"

    ls_info = CalculateRequest(
        batch_size=10,
        total_sample_size=10,
        metrics=[metric_name],
        task_name="regression",
        input_features=[[1, 2], [3, -4], [-5, 6], [1000, 984], [0, 60], [-34, 2222]],
        true_labels=[[1], [2], [3], [4], [5], [6]],
        predicted_labels=[[5], [6], [2], [8], [9], [1]],
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict-low-stability",
        model_api_key="None",
        # TODO: Update metrics library to only require confidence score based on metric, task_name combination
        confidence_scores=[[1]] * 6,
        regression_flag=True
    )

    ls_result = calculate_metrics(ls_info)
    assert isinstance(ls_result.metric_values[metric_name], MetricValue), ls_result

    assert ls_result.metric_values[metric_name].computed_value < 0.9, ls_result
