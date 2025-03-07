from fastapi import HTTPException
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from api.router.api import api
from api.router.rabbitmq import get_jobs_publisher
from api.__init__ import create_application
from common.models.pipeline import PipelineJobType, JobFromAPI, PipelineHalt


# Create a FastAPI TestClient
app = create_application()
client = TestClient(app)


# Mock task_to_metric_map
mock_task_to_metric_map = {
    "binary_classification": ["accuracy", "precision"],
    "multi_class_classification": ["f1_score", "recall"],
    "regression": ["mse", "r2_score"],
}


def test_read_root():
    """Test GET /"""

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the model evaluation server!"}


def test_stop_job():
    """Test POST /stop-job"""

    mock_publisher = MagicMock()
    
    app.dependency_overrides[get_jobs_publisher] = lambda: mock_publisher

    response = client.post("/stop-job", json={"job_id": "1234"})
    
    mock_publisher.publish.assert_called_with(
        JobFromAPI(job_type=PipelineJobType.HALT_JOB, job=PipelineHalt(job_id="1234")).model_dump_json()
    )
    assert response.status_code == 202
    assert response.json() == {"message": "Job stopped"}

    app.dependency_overrides.clear()  # Clean up overrides after the test


def test_stop_job_exception():
    """Test POST /stop-job with an exception"""

    mock_publisher = MagicMock()
    app.dependency_overrides[get_jobs_publisher] = lambda: mock_publisher

    # Simulate an exception when stopping a job
    try:
        with patch(
            "api.router.api.JobFromAPI", side_effect=Exception("RabbitMQ error")
        ):
            client.post("/stop-job", json={"job_id": "1234"})
    except Exception as e:
        assert str(e) == str(
            HTTPException(
                status_code=500, detail="Error during handling of request to /stop-job - RabbitMQ error"
            )
        )

    app.dependency_overrides.clear()  # Clean up overrides after the test


@patch(
    "api.router.api.task_type_to_metric", mock_task_to_metric_map
)  # Use correct module path
def test_retrieve_metric_info():
    """Test GET /retrieve-metric-info"""

    response = client.get("/retrieve-metric-info")

    assert response.status_code == 200
    assert response.json() == {"task_to_metric_map": mock_task_to_metric_map}


def test_generate_metrics_from_info_success():
    with patch("api.router.api.dispatch_job", return_value=None) as mock_dispatch_job:
        """Test POST /evaluate with a valid request"""

        request_data = {
            "dataset_url": "https://example.com/dataset",
            "dataset_api_key": "test_dataset_key",
            "model_url": "https://example.com/model",
            "model_api_key": "test_model_key",
            "metrics": ["accuracy", "precision"],
            "model_type": "binary_classification",
            "user_id": "1234",
        }

        response = client.post("/evaluate", json=request_data)

        assert response.status_code == 202
        assert response.json() == {"message": "Created and dispatched jobs"}
        mock_dispatch_job.assert_called()


def test_generate_metrics_from_info_failure():
    mock_publisher = MagicMock()
    with patch("api.router.api.get_jobs_publisher", return_value=mock_publisher):

        """Test POST /evaluate when dispatching fails"""
        request_data = {
            "dataset_url": "https://example.com/dataset",
            "dataset_api_key": "test_dataset_key",
            "model_url": "https://example.com/model",
            "model_api_key": "test_model_key",
            "metrics": ["accuracy", "precision"],
            "model_type": "binary_classification",
            "user_id": "1234",
        }

        # Simulate an exception when dispatching jobs
        try:
            with patch(
                "api.router.api.dispatch_job", side_effect=Exception("RabbitMQ error")
            ):
                client.post("/evaluate", json=request_data)
        except Exception as e:
            assert str(e) == str(
                HTTPException(
                    status_code=500, detail="Error dispatching jobs - RabbitMQ error"
                )
            )
