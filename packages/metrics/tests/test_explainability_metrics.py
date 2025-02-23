from metrics.models import CalculateRequest
from metrics.metrics import calculate_metrics
from pytest import approx
from tests.server_factory import (
    server_factory,
    HOST,
    server_configs
)

server_factory = server_factory  # To suppress lint errors

# Mock name used to access server_config fields
mock_name = "explanation_metrics"


def test_explanation_stability_similar_scores_result_in_1(server_factory):

    # Names to be tested
    metric_name = "explanation_stability_score"

    with server_factory(mock_name):
        # Check similar predictions after perturbation have value close to 1
        info = CalculateRequest(
            metrics=[metric_name],
            input_features=[[1, 2]],
            confidence_scores=[[0.5]],
            model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict-10000-ESS",
            model_api_key="None"
        )

        result = calculate_metrics(info)
        assert result.metric_values[metric_name] == approx(1.0)


def test_explanation_stability_different_scores_is_not_1(server_factory):
    metric_name = "explanation_stability_score"
    with server_factory(mock_name):
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
def test_explanation_sparsity_ideal_case():
    pass
