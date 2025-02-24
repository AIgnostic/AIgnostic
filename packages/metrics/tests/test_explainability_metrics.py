from metrics.models import CalculateRequest
from metrics.metrics import calculate_metrics
import pytest
from tests.server_factory import (
    server_factory,
    HOST,
    server_configs
)
from tests.metric_mocks.mock_model_explanation_metrics import (
    PERFECT_ESP_INPUT_FEATURES,
    BIVARIATE_ESP_INPUT_FEATURES,
    BIVARIATE_ESP_EXPECTED_SCORE,
    BIVARIATE_ESP_MARGIN,
    BAD_FIDELITY_INPUT_FEATURES,
    BAD_FIDELITY_EXPECTED_SCORE,
    FIDELITY_MARGIN
)
server_factory = server_factory  # To suppress lint errors

# Mock name used to access server_config fields
mock_name = "explanation_metrics"


@pytest.fixture(scope="module")
def apply_server_factory(server_factory):
    with server_factory(mock_name):
        yield


def test_explanation_stability_similar_scores_result_in_1(apply_server_factory):

    # Names to be tested
    metric_name = "explanation_stability_score"

    # Check similar predictions after perturbation have value close to 1
    info = CalculateRequest(
        metrics=[metric_name],
        input_features=[[1, 2]],
        confidence_scores=[[0.5]],
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict-10000-ESS",
        model_api_key="None"
    )

    result = calculate_metrics(info)
    assert result.metric_values[metric_name] == pytest.approx(1.0)


def test_explanation_stability_different_scores_is_not_1(apply_server_factory):
    metric_name = "explanation_stability_score"
    # Check different predictions after perturbation have value close to 0
    info = CalculateRequest(
        metrics=[metric_name],
        input_features=[[1, 2], [3, -4], [-5, 6], [1000, 984], [0, 60], [-34, 2222]],
        confidence_scores=[[0.5], [0.6], [0.2], [0.8], [0.9], [0.1]],
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict-different-ESS",
        model_api_key="None"
    )
    result = calculate_metrics(info)
    assert result.metric_values[metric_name] < 1.0


# TODO: Test explanation sparse and fidelity metrics
def test_explanation_sparsity_ideal_case(apply_server_factory):
    metric_name = "explanation_sparsity_score"
    info = CalculateRequest(
        metrics=[metric_name],
        input_features=PERFECT_ESP_INPUT_FEATURES,
        confidence_scores=[[0.5]] * 10,
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict-perfect-ESP",
        model_api_key="None"
    )
    result = calculate_metrics(info)
    print(result.metric_values[metric_name])
    print(result)
    assert result.metric_values[metric_name] == pytest.approx(1.0)


def test_explanation_sparsity_bivariate_case_classification(apply_server_factory):
    metric_name = "explanation_sparsity_score"
    info = CalculateRequest(
        metrics=[metric_name],
        input_features=BIVARIATE_ESP_INPUT_FEATURES,
        confidence_scores=[[0.8]] * 30,
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict-bivariate-ESP",
        model_api_key="None"
    )
    result = calculate_metrics(info)
    assert result.metric_values[metric_name] == pytest.approx(
        BIVARIATE_ESP_EXPECTED_SCORE,
        BIVARIATE_ESP_MARGIN
    )


def test_good_fidelity(apply_server_factory):
    metric_name = "explanation_fidelity_score"
    feats = [[0.1, 0.2, 0.3, 0.4, 0.5], [1, 2, 3, 4, 5]]
    info = CalculateRequest(
        metrics=[metric_name],
        input_features=feats,  # Required to be in confidence_score format for testing
        predictions=[[1], [10]],
        confidence_scores=[[1], [1]],
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict-perfect-fidelity",
        model_api_key="None"
    )
    result = calculate_metrics(info)
    assert result.metric_values[metric_name] == pytest.approx(1.0, FIDELITY_MARGIN)


def test_low_fidelity(apply_server_factory):
    metric_name = "explanation_fidelity_score"
    info = CalculateRequest(
        metrics=[metric_name],
        input_features=BAD_FIDELITY_INPUT_FEATURES,  # Make input features = confidence scores to enable mock
                                                     # test to produce maximally bad fidelity score
        predictions=[[1]] * len(BAD_FIDELITY_INPUT_FEATURES),
        confidence_scores=BAD_FIDELITY_INPUT_FEATURES,
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict-bad-fidelity",
        model_api_key="None"
    )
    result = calculate_metrics(info)
    assert result.metric_values[metric_name] == pytest.approx(
        BAD_FIDELITY_EXPECTED_SCORE,
        FIDELITY_MARGIN
    )
