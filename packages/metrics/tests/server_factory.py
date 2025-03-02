from tests.metric_mocks.mock_model_finite_diff_grad import app as finite_diff_grad_app
from tests.metric_mocks.mock_model_explanation_metrics import app as expl_stability_app
from tests.metric_mocks.mock_model_ood_auroc import app as ood_auroc_app
from tests.metric_mocks.mock_text_inp_classifier_expl_stability import app as txt_inp_expl_stability_app
from mocks.model.finbert import app as finbert_app
from threading import Thread
import pytest
import uvicorn
import time
import contextlib


HOST = "127.0.0.1"

# Server_configs maps a mock model to a port and app
server_configs = {
    "finite_diff_grad": {
        "port": 3000,
        "app": finite_diff_grad_app,
    },
    "ood_auroc": {
        "port": 3001,
        "app": ood_auroc_app,
    },
    "explanation_metrics": {
        "port": 3002,
        "app": expl_stability_app,
    },
    "txt_inp_expl_stability": {
        "port": 3003,
        "app": txt_inp_expl_stability_app,
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
