import pytest
from fastapi.testclient import TestClient
import os
import uuid
import json
from user_added_metrics.metric_server import app  # Import FastAPI app from your script

client = TestClient(app)

# Temporary file paths
TMP_DIR = "/tmp/test_user_added_metrics"
os.makedirs(TMP_DIR, exist_ok=True)

@pytest.fixture
def sample_requirements():
    """Creates a unique requirements.txt file for testing."""
    req_file_path = os.path.join(TMP_DIR, f"requirements_{uuid.uuid4().hex}.txt")
    with open(req_file_path, "w") as f:
        f.write("numpy\n")
    return req_file_path

@pytest.fixture
def sample_script():
    """Creates a temporary user script file for testing."""
    script_file_path = os.path.join(TMP_DIR, "test_script.py")
    with open(script_file_path, "w") as f:
        f.write("""
import numpy as np

def add_numbers(a, b):
    return a + b

def multiply_matrix(matrix):
    np_matrix = np.array(matrix)
    return (np_matrix * 2).tolist()
""")
    return script_file_path

def test_upload_dependencies(sample_requirements):
    """Test uploading dependencies."""
    with open(sample_requirements, "rb") as f:
        response = client.post("/upload-dependencies", files={"file": f})
    assert response.status_code == 200
    json_response = response.json()
    assert "file_id" in json_response
    assert json_response["message"] == "Dependencies installed successfully"
    # Verify that the virtual environment folder exists
    assert os.path.exists(os.path.join("/tmp/venvs", json_response["file_id"]))

def test_upload_metrics(sample_script, sample_requirements):
    """Test uploading a metrics script."""
    # First, upload dependencies to obtain a file_id.
    with open(sample_requirements, "rb") as f:
        dep_response = client.post("/upload-dependencies", files={"file": f})
    assert dep_response.status_code == 200
    file_id = dep_response.json()["file_id"]

    # Now, upload the script with the obtained file_id.
    with open(sample_script, "rb") as f:
        script_response = client.post(f"/upload-metrics?file_id={file_id}", files={"file": f})
    assert script_response.status_code == 200
    json_response = script_response.json()
    assert json_response["message"] == "Metrics uploaded successfully"
    assert "functions" in json_response
    assert "add_numbers" in json_response["functions"]
    assert "multiply_matrix" in json_response["functions"]

def test_execute_function(sample_script, sample_requirements):
    """Test executing a user-defined function."""
    # Upload dependencies
    with open(sample_requirements, "rb") as f:
        dep_response = client.post("/upload-dependencies", files={"file": f})
    assert dep_response.status_code == 200
    file_id = dep_response.json()["file_id"]

    # Upload the user script
    with open(sample_script, "rb") as f:
        script_response = client.post(f"/upload-metrics?file_id={file_id}", files={"file": f})
    assert script_response.status_code == 200

    # Execute the 'add_numbers' function with parameters.
    # Note: use "params" instead of "args" and post to "/compute-metric"
    payload = {
        "file_id": file_id,
        "function_name": "add_numbers",
        "params": {"a": 1, "b": 2}
    }
    exec_response = client.post("/compute-metric", json=payload)
    assert exec_response.status_code == 200
    json_response = exec_response.json()
    # The endpoint returns a JSON-stringified result.
    result = json.loads(json_response["result"])
    assert result == 3


def test_execute_numpy_function(sample_script, sample_requirements):
    """Test executing a user-defined numpy function."""
    # Upload dependencies
    with open(sample_requirements, "rb") as f:
        dep_response = client.post("/upload-dependencies", files={"file": f})
    assert dep_response.status_code == 200
    file_id = dep_response.json()["file_id"]

    # Upload the user script
    with open(sample_script, "rb") as f:
        script_response = client.post(f"/upload-metrics?file_id={file_id}", files={"file": f})
    assert script_response.status_code == 200

    # Execute the 'multiply_matrix' function with parameters.
    payload = {
        "file_id": file_id,
        "function_name": "multiply_matrix",
        "params": {"matrix": [[1, 2], [3, 4]]}
    }
    exec_response = client.post("/compute-metric", json=payload)
    assert exec_response.status_code == 200
    json_response = exec_response.json()
    # The endpoint returns a JSON-stringified result.
    result = json.loads(json_response["result"])
    assert result == [[2, 4], [6, 8]]
