import pytest
from fastapi.testclient import TestClient
import os
import uuid
from user_added_metrics.metric_server import app


client = TestClient(app)


# Temporary file paths
TMP_DIR = "/tmp/test_user_added_metrics"
os.makedirs(TMP_DIR, exist_ok=True)


@pytest.fixture
def sample_requirements():
    """Creates a unique requirements.txt file for testing."""
    req_file_path = os.path.join(TMP_DIR, f"requirements_{uuid.uuid4().hex}.txt")
    # For testing purposes, include a package that is not used by our script
    with open(req_file_path, "w") as f:
        f.write("pika\n")
    return req_file_path


@pytest.fixture
def sample_script():
    """Creates a temporary user script file for testing that conforms to the expected interface."""
    script_file_path = os.path.join(TMP_DIR, "test_script.py")
    with open(script_file_path, "w") as f:
        f.write(
            """
import numpy as np

def metric_add_numbers(data):
    a = data.get("a")
    b = data.get("b")
    computed = a + b
    # For this example, we assume ideal_value is equal to computed and range is a list with the computed value repeated.
    return {
        "computed_value": computed,
        "ideal_value": computed,
        "range": [computed, computed]
    }

def metric_multiply_matrix(data):
    matrix = data.get("matrix")
    np_matrix = np.array(matrix)
    computed = (np_matrix * 2).tolist()
    # Compute a range from the flattened matrix values.
    flat = [item for sub in computed for item in sub]
    return {
        "computed_value": computed,
        "ideal_value": computed,
        "range": [min(flat), max(flat)]
    }
"""
        )
    return script_file_path


def test_upload_metrics_and_dependencies(sample_script, sample_requirements):
    """Test uploading metrics and dependencies."""
    user_id = str(uuid.uuid4())

    with open(sample_requirements, "rb") as req_file, open(sample_script, "rb") as script_file:
        response = client.post(
            f"/upload-metrics-and-dependencies?user_id={user_id}",
            files={"requirements": req_file, "script": script_file},
        )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["user_id"] == user_id
    assert json_response["message"] == "Metrics and dependencies uploaded successfully"
    assert "functions" in json_response
    # Verify that both functions starting with "metric_" are present.
    functions = json_response["functions"]
    assert "metric_add_numbers" in functions
    assert "metric_multiply_matrix" in functions


def test_inspect_functions(sample_script, sample_requirements):
    """Test inspecting the functions uploaded by the user."""
    user_id = str(uuid.uuid4())

    with open(sample_requirements, "rb") as req_file, open(sample_script, "rb") as script_file:
        response = client.post(
            f"/upload-metrics-and-dependencies?user_id={user_id}",
            files={"requirements": req_file, "script": script_file},
        )

    assert response.status_code == 200
    inspect_response = client.get(f"/inspect-uploaded-functions/{user_id}")
    assert inspect_response.status_code == 200
    json_response = inspect_response.json()
    assert json_response["user_id"] == user_id
    functions = json_response["functions"]
    assert "metric_add_numbers" in functions
    assert "metric_multiply_matrix" in functions


def test_execute_function(sample_script, sample_requirements):
    """Test executing a user-defined function that adds numbers."""
    user_id = str(uuid.uuid4())

    with open(sample_requirements, "rb") as req_file, open(sample_script, "rb") as script_file:
        response = client.post(
            f"/upload-metrics-and-dependencies?user_id={user_id}",
            files={"requirements": req_file, "script": script_file},
        )

    assert response.status_code == 200

    payload = {
        "user_id": user_id,
        "function_name": "metric_add_numbers",
        "params": {"a": 1, "b": 2}
    }
    exec_response = client.post("/compute-metric", json=payload)
    assert exec_response.status_code == 200
    json_response = exec_response.json()
    # The response is of the form: {"result": { ... }}
    result = json_response["result"]
    result = result["result"]

    # Expected values: computed_value=3, ideal_value=3, range=[3,3]
    assert result["computed_value"] == 3
    assert result["ideal_value"] == 3
    assert result["range"] == [3, 3]


def test_execute_numpy_function(sample_script, sample_requirements):
    """Test executing a user-defined function that multiplies a matrix using numpy."""
    user_id = str(uuid.uuid4())
    with open(sample_requirements, "rb") as req_file, open(sample_script, "rb") as script_file:
        response = client.post(
            f"/upload-metrics-and-dependencies?user_id={user_id}",
            files={"requirements": req_file, "script": script_file},
        )
    assert response.status_code == 200

    payload = {
        "user_id": user_id,
        "function_name": "metric_multiply_matrix",
        "params": {"matrix": [[1, 2], [3, 4]]}
    }
    exec_response = client.post("/compute-metric", json=payload)
    assert exec_response.status_code == 200
    json_response = exec_response.json()
    result = json_response["result"]
    # Expected computed matrix is [[2,4],[6,8]] and the range from these values is [2, 8].
    expected_matrix = [[2, 4], [6, 8]]
    print(result)
    result = result["result"]
    assert result["computed_value"] == expected_matrix
    assert result["ideal_value"] == expected_matrix
    assert result["range"] == [2, 8]


def test_clear_user_data(sample_script, sample_requirements):
    """Test clearing user-specific data."""
    user_id = str(uuid.uuid4())
    with open(sample_requirements, "rb") as req_file, open(sample_script, "rb") as script_file:
        response = client.post(
            f"/upload-metrics-and-dependencies?user_id={user_id}",
            files={"requirements": req_file, "script": script_file},
        )
    assert response.status_code == 200

    clear_response = client.delete(f"/clear-user-data/{user_id}")
    assert clear_response.status_code == 200
    json_response = clear_response.json()
    assert json_response["message"] == f"Data for user {user_id} cleared successfully"
