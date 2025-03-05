from metrics.models import CalculateRequest, MetricValue
from metrics.metrics import calculate_metrics
import pytest
from tests.server_factory import (
    server_factory,
    server_configs,
    HOST
)

server_factory = server_factory  # To suppress lint errors

mock_name = "tinystories_integration"


@pytest.fixture(scope="module")
def apply_server_factory(server_factory):
    with server_factory(mock_name):
        yield


def test_tinystories_works_with_explanation_metrics(apply_server_factory):
    metrics = ["expl_stability_text_input"]

    features = [["Once upon a time, in a land far, far away, there was a magical forest where"]]
    labels = [["every creature lived in harmony, and the trees whispered secrets of ancient times."]]

    # features = [["We can't go over it! We can't go under it!"]]
    # labels = [["Oh no! We've got to go through it!"]]

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
        task_name="next_token_generation"
    )

    result = calculate_metrics(info)
    print(result)
    assert isinstance(result.metric_values["expl_stability_text_input"], MetricValue), result
    value = result.metric_values["expl_stability_text_input"].computed_value
    assert 0 <= value <= 1, result
