from metrics.models import CalculateRequest
from tests.metric_mocks.mock_model_finite_diff_grad import app as finite_diff_grad_app
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
        "port": 3333,
        "app": finite_diff_grad_app,
    },
    "ood_auroc": {
        "port": 3334,
        "app": ood_auroc_app,
    }
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


def test_explanation_stability_scores(server_factory):
    pass


@pytest.mark.asyncio
async def test_finite_diff_gradient(server_factory):
    pass


# @pytest.mark.skip("Failing - pydantic model validation errors")
@pytest.mark.asyncio
async def test_ood_auroc(server_factory):
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
        )

        result = await calculate_metrics(info)
        result = result.metric_values["ood_auroc"]

        assert isinstance(result, float), f"Expected AUROC to be a float, but got {type(result)}"
        assert 0.0 <= result <= 1.0, f"Expected AUROC to be between 0.0 and 1.0, but got {result}"
