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
        f.write("pika \n")
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

def test_upload_metrics_and_dependencies(sample_script, sample_requirements):
    """Test uploading metrics and dependencies."""
    with open(sample_requirements, "rb") as req_file, open(sample_script, "rb") as script_file:
        response = client.post("/upload-metrics-and-dependencies", files={"requirements": req_file, "script": script_file})
    assert response.status_code == 200
    json_response = response.json()
    assert "file_id" in json_response
    assert json_response["message"] == "Metrics and dependencies uploaded successfully"
    assert "functions" in json_response
    assert "add_numbers" in json_response["functions"]
    assert "multiply_matrix" in json_response["functions"]
    # Verify that the virtual environment folder exists
    assert os.path.exists(os.path.join("/tmp/venvs", json_response["file_id"]))
    # Verify that the script file exists
    safe_file_id = json_response["file_id"].replace("-", "_")
    assert os.path.exists(os.path.join("/tmp/user_added_metrics", f"user_script_{safe_file_id}.py"))


def test_inspect_functions(sample_script, sample_requirements):
    """Test inspecting the functions uploaded by the user."""
    with open(sample_requirements, "rb") as req_file, open(sample_script, "rb") as script_file:
        response = client.post("/upload-metrics-and-dependencies", files={"requirements": req_file, "script": script_file})
    assert response.status_code == 200
    file_id = response.json()["file_id"]

    inspect_response = client.get(f"/inspect-uploaded-functions/{file_id}")
    assert inspect_response.status_code == 200
    json_response = inspect_response.json()
    assert json_response["file_id"] == file_id
    assert "add_numbers" in json_response["functions"]
    assert "multiply_matrix" in json_response["functions"]
    
def test_upload_metrics_no_dependencies(sample_script):
    """Test uploading metrics without dependencies."""
    with open(sample_script, "rb") as script_file:
        response = client.post("/upload-metrics-and-dependencies", files={"script": script_file})
    assert response.status_code == 200
    json_response = response.json()
    assert "file_id" in json_response
    assert json_response["message"] == "Metrics and dependencies uploaded successfully"
    assert "functions" in json_response
    assert "add_numbers" in json_response["functions"]
    assert "multiply_matrix" in json_response["functions"]
    # Verify that the virtual environment folder exists
    assert os.path.exists(os.path.join("/tmp/venvs", json_response["file_id"]))
    # Verify that the script file exists
    safe_file_id = json_response["file_id"].replace("-", "_")
    assert os.path.exists(os.path.join("/tmp/user_added_metrics", f"user_script_{safe_file_id}.py"))

def test_execute_function_no_dependencies(sample_script):
    """Test executing a user-defined function without dependencies."""
    with open(sample_script, "rb") as script_file:
        response = client.post("/upload-metrics-and-dependencies", files={"script": script_file})
    assert response.status_code == 200
    file_id = response.json()["file_id"]

    payload = {
        "file_id": file_id,
        "function_name": "add_numbers",
        "params": {"a": 1, "b": 2}
    }
    exec_response = client.post("/compute-metric", json=payload)
    assert exec_response.status_code == 200
    json_response = exec_response.json()
    result = json.loads(json_response["result"])
    assert result == 3

def test_execute_function(sample_script, sample_requirements):
    """Test executing a user-defined function."""
    with open(sample_requirements, "rb") as req_file, open(sample_script, "rb") as script_file:
        response = client.post("/upload-metrics-and-dependencies", files={"requirements": req_file, "script": script_file})
    assert response.status_code == 200
    file_id = response.json()["file_id"]

    payload = {
        "file_id": file_id,
        "function_name": "add_numbers",
        "params": {"a": 1, "b": 2}
    }
    exec_response = client.post("/compute-metric", json=payload)
    assert exec_response.status_code == 200
    json_response = exec_response.json()
    result = json.loads(json_response["result"])
    assert result == 3

def test_execute_numpy_function(sample_script, sample_requirements):
    """Test executing a user-defined numpy function."""
    with open(sample_requirements, "rb") as req_file, open(sample_script, "rb") as script_file:
        response = client.post("/upload-metrics-and-dependencies", files={"requirements": req_file, "script": script_file})
    assert response.status_code == 200
    file_id = response.json()["file_id"]

    payload = {
        "file_id": file_id,
        "function_name": "multiply_matrix",
        "params": {"matrix": [[1, 2], [3, 4]]}
    }
    exec_response = client.post("/compute-metric", json=payload)
    assert exec_response.status_code == 200
    json_response = exec_response.json()
    result = json.loads(json_response["result"])
    assert result == [[2, 4], [6, 8]]


def test_clear_server(sample_script, sample_requirements):
    """Test clearing the server."""
    # Upload metrics and dependencies
    with open(sample_requirements, "rb") as req_file, open(sample_script, "rb") as script_file:
        response = client.post("/upload-metrics-and-dependencies", files={"requirements": req_file, "script": script_file})
    assert response.status_code == 200

    # Clear the server
    clear_response = client.delete("/clear-server")
    assert clear_response.status_code == 200
    json_response = clear_response.json()
    assert json_response["message"] == "Server cleared successfully"
    # Verify that the upload and venv directories are empty
    assert not os.listdir("/tmp/user_added_metrics")
    assert not os.listdir("/tmp/venvs")
