from metrics.models import CalculateRequest
from metrics.utils import _finite_difference_gradient
from tests.metric_mocks.mock_model_finite_diff_grad import (
    app as finite_diff_grad_app,
    TEST_INPUT,
    EPSILON,
    EXPECTED_GRADIENT
)
from tests.metric_mocks.mock_model_explaination_stability import app as expl_stability_app
from tests.metric_mocks.mock_model_ood_auroc import app as ood_auroc_app
from metrics.metrics import calculate_metrics
from threading import Thread
import numpy as np
import pytest
import uvicorn
import time
import contextlib


HOST = "127.0.0.1"

server_configs = {
    "finite_diff_grad": {
        "port": 3000,
        "app": finite_diff_grad_app,
    },
    "ood_auroc": {
        "port": 3001,
        "app": ood_auroc_app,
    },
    "explanation_stability_score": {
        "port": 3002,
        "app": expl_stability_app,
    },
}


@pytest.fixture(scope="module")
def server_factory():
    servers = []

    def start_server(server):
        server.run()

    @contextlib.contextmanager
    def run_server(server_name):
        config_info = server_configs[server_name]
        model_config = uvicorn.Config(app=config_info["app"], host=HOST, port=config_info["port"])
        model_server = uvicorn.Server(model_config)

        thread = Thread(target=start_server, args=(model_server,), daemon=True)
        thread.start()
        time.sleep(2)  # Wait for the servers to start
        assert model_server.started

        servers.append((model_server, thread))

        yield
        model_server.should_exit = True
        thread.join()
    yield run_server

    # Cleanup any remaining servers
    for server, thread in servers:
        if not server.should_exit:
            server.should_exit = True
            thread.join()


def test_explanation_stability_similar_scores_result_in_1(server_factory):
    metric_name = "explanation_stability_score"
    with server_factory(metric_name):
        # Check similar predictions after perturbation have value close to 1
        info = CalculateRequest(
            metrics=[metric_name],
            input_features=[[1, 2]],
            confidence_scores=[[0.5]],
            model_url=f"http://{HOST}:{server_configs[metric_name]['port']}/predict-10000",
            model_api_key="None"
        )
        result = calculate_metrics(info)
        assert result.metric_values[metric_name] == pytest.approx(1.0)


def test_explanation_stability_different_scores_is_not_1(server_factory):
    metric_name = "explanation_stability_score"
    with server_factory(metric_name):
        # Check different predictions after perturbation have value close to 0
        info = CalculateRequest(
            metrics=[metric_name],
            input_features=[[1, 2], [3, -4], [-5, 6], [1000, 984], [0, 60], [-34, 2222]],
            confidence_scores=[[0.5], [0.6], [0.2], [0.8], [0.9], [0.1]],
            model_url=f"http://{HOST}:{server_configs[metric_name]['port']}/predict-different",
            model_api_key="None"
        )
        result = calculate_metrics(info)
        assert result.metric_values[metric_name] < 1.0


def test_finite_diff_gradient(server_factory):
    metric_name = "finite_diff_grad"
    with server_factory(metric_name):
        info = CalculateRequest(
            metrics=[metric_name],
            input_features=TEST_INPUT,
            model_url=f"http://{HOST}:{server_configs[metric_name]['port']}/predict",
        )

        result = _finite_difference_gradient(info, EPSILON)

        assert len(result) == len(TEST_INPUT), (
            f"Expected gradient to have {len(TEST_INPUT)} samples, but got {len(result)}"
        )
        assert len(result[0]) == len(TEST_INPUT[0]), (
            f"Expected gradient to have {len(TEST_INPUT[0])} features, but got {len(result[0])}"
        )
        assert result.tolist() == EXPECTED_GRADIENT, (
            f"Expected gradient to be {EXPECTED_GRADIENT}, but got {result}"
        )


def test_ood_auroc(server_factory):
    metric_name = "ood_auroc"
    with server_factory(metric_name):
        input_data = np.random.rand(100, 10).tolist()  # 100 samples, 10 features
        confidence_scores = np.random.uniform(0, 1, 100).tolist()  # 100 ID confidence scores
        confidence_scores = [[score] for score in confidence_scores]
        info = CalculateRequest(
            metrics=[metric_name],
            input_features=input_data,
            confidence_scores=confidence_scores,
            model_url=f"http://{HOST}:{server_configs[metric_name]['port']}/predict",
            model_api_key="None"
        )

        result = calculate_metrics(info)
        result = result.metric_values["ood_auroc"]

        assert isinstance(result, float), f"Expected AUROC to be a float, but got {type(result)}"
        assert 0.0 <= result <= 1.0, f"Expected AUROC to be between 0.0 and 1.0, but got {result}"


# TODO: Test explanation sparse and fidelity metrics
