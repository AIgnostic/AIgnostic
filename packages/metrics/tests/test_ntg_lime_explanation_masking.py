from metrics.models import CalculateRequest, MetricValue
from common.models import ModelResponse, ModelInput
import pytest
from tests.server_factory import (
    server_factory,
    HOST,
    server_configs
)
from mocks.model.finbert import app as finbert_app
from fastapi.testclient import TestClient
from metrics.metrics import calculate_metrics
import requests

finbert_client = TestClient(finbert_app)
server_factory = server_factory  # To suppress lint errors

# Mock name used to access server_config fields
mock_name = "ntg_explanation_metrics_lime"

test_data = {
    "high_stability": ModelInput(
        features=[
            ["The company's shares rose 20 pc after the announcement of the new product line."],
            ["The quarterly earnings report exceeded analysts' expectations, driving the stock price up significantly."],
            ["The market remained flat as investors awaited the Federal Reserve's decision."],
            ["The company's CEO resigned amid allegations of financial misconduct, causing shares to plummet drastically."],
            ["The new merger is expected to create significant synergies and boost profitability substantially."],
            # ["The economic outlook remains steady with little growth or decline."],
            # ["The company's innovative product received overwhelmingly positive reviews, leading to increased investor confidence."],
            # ["The unexpected drop in sales led to a severe downward revision of the company's revenue forecast."],
            # ["The company's groundbreaking technology is expected to revolutionize the industry, attracting major investments."],
            # ["The company's bankruptcy filing caused a massive sell-off, leading to a sharp decline in stock prices."]
        ],
        labels=[
            ['positive'],
            ['positive'],
            ['neutral'],
            ['negative'],
            ['positive'],
            # ['neutral'],
            # ['positive'],
            # ['negative'],
            # ['positive'],
            # ['negative']
        ],
        group_ids = [0] * 10
    ),
    "low_stability": ModelInput(
        # more ambiguous statements than the high stability version
        features=[
            ["The company's revenue growth slowed, but still outpaced industry averages."],
            ["Despite market volatility, the stock maintained its position within a narrow range."],
            ["The new product launch received mixed reviews, yet sales figures exceeded initial projections."],
            ["Regulatory changes impacted short-term profits, though long-term outlook remains optimistic."],
            ["The unexpected merger announcement left investors uncertain about future performance."],
            # ["Cost-cutting measures improved margins, but raised concerns about product quality."],
            # ["The company's market share declined slightly, while overall sector growth accelerated."],
            # ["Quarterly earnings met expectations, but guidance for the next quarter was revised downward."],
            # ["The CEO's controversial statements led to a temporary stock dip before recovering."],
            # ["A major contract was lost, but the company secured several smaller, potentially lucrative deals."]
        ],
        labels=[
            ['neutral'],
            ['neutral'],
            ['positive'],
            ['positive'],
            ['neutral'],
            # ['neutral'],
            # ['neutral'],
            # ['neutral'],
            # ['neutral'],
            # ['neutral']
        ],
        group_ids = [0] * 10
    ),
}


@pytest.fixture(scope="module")
def apply_server_factory(server_factory):
    with server_factory(mock_name):
        yield


def test_ntg_explanation_stability(apply_server_factory):
    metric_name = "expl_stability_text_input"
    hs_data = test_data["high_stability"]

    response = finbert_client.post("/predict", json=hs_data.model_dump(mode="json"))
    assert response.status_code == 200, response.text
    
    model_resp: ModelResponse = response.json()
    assert model_resp["confidence_scores"], model_resp

    # Check similar predictions after perturbation have value close to 1
    hs_info = CalculateRequest(
        batch_size=10,
        total_sample_size=10,
        metrics=[metric_name],
        input_features=hs_data.features,
        confidence_scores=model_resp["confidence_scores"],
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict",
        model_api_key="None"
    )

    hs_result = calculate_metrics(hs_info)

    ls_data = test_data["low_stability"]
    response = finbert_client.post("/predict", json=ls_data.model_dump(mode="json"))
    assert response.status_code == 200, response.text

    model_resp: ModelResponse = response.json()
    assert model_resp["confidence_scores"], model_resp

    ls_info = CalculateRequest(
        batch_size=10,
        total_sample_size=10,
        metrics=[metric_name],
        input_features=ls_data.features,
        confidence_scores=model_resp["confidence_scores"],
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict",
    )

    ls_result = calculate_metrics(ls_info)

    assert isinstance(hs_result.metric_values[metric_name], MetricValue), hs_result
    assert isinstance(ls_result.metric_values[metric_name], MetricValue), ls_result

    assert (
        hs_result.metric_values[metric_name].computed_value
        > ls_result.metric_values[metric_name].computed_value
    ), "Stronger examples should have higher stability scores than ambiguous datapoints"