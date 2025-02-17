from metrics.models import CalculateRequest
from tests.mock_model import app as mock_model
from metrics.metrics import calculate_metrics
from threading import Thread
import numpy as np
import pytest
import uvicorn
import time


model_url = "http://127.0.0.1:3334/get-prediction-and-confidence"


@pytest.fixture(scope="module")
def run_servers():
    model_config = uvicorn.Config(app=mock_model, host="127.0.0.1", port=3334)
    model_server = uvicorn.Server(model_config)

    def start_server(server):
        server.run()

    thread = Thread(target=start_server, args=(model_server,), daemon=True)
    thread.start()
    time.sleep(2)  # Wait for the servers to start

    assert model_server.started

    yield
    model_server.should_exit = True
    thread.join()


@pytest.mark.skip("Failing - pydantic model validation errors")
@pytest.mark.asyncio
async def test_ood_auroc(run_servers):
    input_data = np.random.rand(10, 10).tolist()  # 100 samples, 10 features
    confidence_scores = np.random.uniform(0, 1, 10).tolist()  # 100 ID confidence scores
    confidence_scores = [[score] for score in confidence_scores]
    info = CalculateRequest(
        metrics=["ood_auroc"],
        input_data=input_data,
        confidence_scores=confidence_scores,
        model_url=model_url,
    )

    result = await calculate_metrics(info)
    result = result.metric_values["ood_auroc"]

    assert isinstance(result, float), f"Expected AUROC to be a float, but got {type(result)}"
    assert 0.0 <= result <= 1.0, f"Expected AUROC to be between 0.0 and 1.0, but got {result}"
