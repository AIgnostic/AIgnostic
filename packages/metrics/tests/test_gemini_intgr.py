from metrics.models import CalculateRequest, TaskType
from metrics.metrics import calculate_metrics
import pytest
from tests.server_factory import (
    server_factory,
    server_configs,
    HOST
)

server_factory = server_factory  # To suppress lint errors

mock_name = "gemini_integration"


@pytest.fixture(scope="module")
def apply_server_factory(server_factory):
    with server_factory(mock_name):
        yield


@pytest.mark.skip(reason="Cannot run test due to API Usage Limits")
def test_gemini_works_with_explanation_metrics(apply_server_factory):
    metrics = ["expl_stability_text_input"]

    features = [["Respond with the exact output: \"Hello world\""]]
    labels = [["Hello world"]]

    info = CalculateRequest(
        batch_size=1,
        total_sample_size=1,
        metrics=metrics,
        input_features=features,
        true_labels=labels,
        predicted_labels=labels,
        # TODO: remove confidence scores requirement
        confidence_scores=[[1.0]],
        model_url=f"http://{HOST}:{server_configs[mock_name]['port']}/predict",
        model_api_key="None",  # Key passed directly to mock for testing other functionality
        task_name=TaskType.NEXT_TOKEN_GENERATION
    )

    result = calculate_metrics(info)
    print(result)
    assert isinstance(result.metric_values["expl_stability_text_input"], float), result
    assert 0 <= result.metric_values["expl_stability_text_input"] <= 1, result
