from metrics.models import CalculateRequest, MetricValue
from common.models import ModelResponse
import pytest
from tests.server_factory import (
    server_factory,
    HOST,
    server_configs
)
from fastapi.testclient import TestClient
from metrics.metrics import calculate_metrics
from tests.metric_mocks.mock_text_inp_classifier_expl_stability import TEST_INPUT

server_factory = server_factory  # To suppress lint errors

# Mock name used to access server_config fields
mock_name = "txt_inp_expl_stability"
client = TestClient(server_configs[mock_name]["app"])


@pytest.fixture(scope="module")
def apply_server_factory(server_factory):
    with server_factory(mock_name):
        yield


def test_ntg_explanation_stability(apply_server_factory):
    metric_name = "expl_stability_text_input"

    response = client.post("/predict-hs", json=TEST_INPUT.model_dump(mode="json"))
    assert response.status_code == 200, response.text

    model_resp: ModelResponse = response.json()
    assert model_resp["confidence_scores"], model_resp

    # Check similar predictions after perturbation have value close to 1
    hs_info = CalculateRequest(
        batch_size=10,
        total_sample_size=10,
        metrics=[metric_name],
        input_features=TEST_INPUT.features,
        confidence_scores=model_resp["confidence_scores"],
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict-hs",
        model_api_key="None",
        task_name="text_classification",
    )

    hs_result = calculate_metrics(hs_info)
    assert isinstance(hs_result.metric_values[metric_name], MetricValue), hs_result

    response = client.post("/predict-ls", json=TEST_INPUT.model_dump(mode="json"))
    assert response.status_code == 200, response.text

    model_resp: ModelResponse = response.json()
    assert model_resp["confidence_scores"], model_resp

    ls_info = CalculateRequest(
        batch_size=10,
        total_sample_size=10,
        metrics=[metric_name],
        input_features=TEST_INPUT.features,
        confidence_scores=model_resp["confidence_scores"],
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict-ls",
        model_api_key="None",
        task_name="text_classification",
    )

    ls_result = calculate_metrics(ls_info)

    assert isinstance(ls_result.metric_values[metric_name], MetricValue), ls_result

    assert (
        hs_result.metric_values[metric_name].computed_value
        > ls_result.metric_values[metric_name].computed_value
    ), "Stronger examples should have higher stability scores than ambiguous datapoints"


def test_high_stability_score(apply_server_factory):
    metric_name = "expl_stability_text_input"

    response = client.post("/predict-hs", json=TEST_INPUT.model_dump(mode="json"))

    model_resp: ModelResponse = response.json()
    assert model_resp["confidence_scores"], model_resp

    hs_info = CalculateRequest(
        batch_size=10,
        total_sample_size=10,
        metrics=[metric_name],
        input_features=TEST_INPUT.features,
        confidence_scores=model_resp["confidence_scores"],
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict-hs",
        model_api_key="None",
        task_name="text_classification"
    )

    hs_result = calculate_metrics(hs_info)
    assert isinstance(hs_result.metric_values[metric_name], MetricValue), hs_result

    assert hs_result.metric_values[metric_name].computed_value == 1.0, hs_result
