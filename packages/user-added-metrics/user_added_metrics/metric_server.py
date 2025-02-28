import subprocess
from fastapi import FastAPI, UploadFile, File, HTTPException
import importlib.util
import os 
import shutil
from common.models.common import ComputeUserMetricRequest
import uvicorn 
import uuid
from pydantic import BaseModel

app = FastAPI()

UPLOAD_DIR = "/tmp/user_added_metrics"
os.makedirs(UPLOAD_DIR, exist_ok=True)

VENV_DIR = "/tmp/venvs"
os.makedirs(VENV_DIR, exist_ok=True)


# store loaded user functions
user_functions = {}

def create_virtual_env(env_path):
    """Creates a virtual environment at the specified path."""
    subprocess.run(["python3", "-m", "venv", env_path], check=True)

def install_dependencies(env_path, requirements_path):
    """Installs dependencies from requirements.txt into the virtual environment."""
    pip_path = os.path.join(env_path, "bin", "pip")
    subprocess.run([pip_path, "install", "-r", requirements_path], check=True)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the user added metrics server!"}

@app.post("/upload-dependencies")
async def upload_dependencies(file: UploadFile = File(...)):
    """Uploads and installs dependencies from a user-provided requirements.txt."""

    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="File must be a .txt file")
    
    file_id = str(uuid.uuid4()) 
    env_path = os.path.join(VENV_DIR, file_id)
    os.makedirs(env_path, exist_ok=True)

    # create virtual environment
    create_virtual_env(env_path)

    # save requirements.txt
    requirements_path = os.path.join(env_path, "requirements.txt")
    with open(requirements_path, "wb") as f:
        shutil.copyfileobj(file.file, f)    

    # install dependencies
    install_dependencies(env_path, requirements_path)

    # Install numpy by default unless already in dependencies
    with open(requirements_path, "r") as f:
        requirements = f.read()
    
    if "numpy" not in requirements:
        pip_path = os.path.join(env_path, "bin", "pip")
        subprocess.run([pip_path, "install", "numpy"], check=True)

    return {"message": "Dependencies installed successfully", "file_id": file_id}

import sys

@app.post("/upload-metrics")
async def upload_metrics(file_id: str, file: UploadFile = File(...)):
    """Uploads a user script and loads functions inside the corresponding virtual environment."""
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="File must be a .py file")

    safe_file_id = file_id.replace("-", "_")  # Convert dashes to underscores
    script_path = os.path.join(UPLOAD_DIR, f"user_script_{safe_file_id}.py")

    with open(script_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Add script directory to sys.path before importing
    sys.path.insert(0, UPLOAD_DIR)

    # Load the module dynamically
    module_name = f"user_script_{safe_file_id}"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Store callable functions
    user_functions[file_id] = {
        name: func for name, func in vars(module).items() if callable(func)
    }

    return {"message": "Metrics uploaded successfully", "functions": list(user_functions[file_id].keys())}


@app.post("/compute-metric")
async def compute_metric(data: ComputeUserMetricRequest):
    """Executes a user-defined function inside its corresponding virtual environment."""
    file_id = data.file_id
    function_name = data.function_name
    params = data.params

    if file_id not in user_functions or function_name not in user_functions[file_id]:
        raise HTTPException(status_code=404, detail="Function not found")

    env_path = os.path.join(VENV_DIR, file_id)
    python_bin = os.path.join(env_path, "bin", "python")

    safe_file_id = file_id.replace("-", "_")  # Convert dashes to underscores

    # Ensure Python can find the script
    sys.path.insert(0, UPLOAD_DIR)

    script_code = f"""
import sys
import json
sys.path.insert(0, '{UPLOAD_DIR}')
from user_script_{safe_file_id} import {function_name} as func
result = func(**{params})
print(json.dumps(result))
"""

    process = subprocess.run(
        [python_bin, "-c", script_code], capture_output=True, text=True
    )

    if process.returncode != 0:
        raise HTTPException(status_code=500, detail=process.stderr)

    return {"result": process.stdout.strip()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)