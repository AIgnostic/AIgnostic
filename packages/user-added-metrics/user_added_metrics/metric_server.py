import json
import subprocess
from fastapi import FastAPI, UploadFile, File, HTTPException
import importlib.util
import os 
import shutil
from common.models.common import ComputeUserMetricRequest
import uvicorn 
import uuid
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import numpy as np
import resource

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/tmp/user_added_metrics"
os.makedirs(UPLOAD_DIR, exist_ok=True)

VENV_DIR = "/tmp/venvs"
os.makedirs(VENV_DIR, exist_ok=True)


# store loaded user functions
user_functions = {}

def get_user_path(base_dir, user_id):
    """Generates a user-specific directory path."""
    return os.path.join(base_dir, user_id)

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


@app.post("/upload-metrics-and-dependencies")
async def upload_metrics_and_dependencies(user_id: str, requirements: UploadFile = File(None), script: UploadFile = File(...)):
    """Uploads a user script and its dependencies, then loads functions inside the corresponding virtual environment."""
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    if requirements and not requirements.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Requirements file must be a .txt file")
    
    if not script.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Script file must be a .py file")
    
    user_upload_dir = get_user_path(UPLOAD_DIR, user_id)
    user_venv_dir = get_user_path(VENV_DIR, user_id)
    os.makedirs(user_upload_dir, exist_ok=True)
    os.makedirs(user_venv_dir, exist_ok=True)

    # Create virtual environment
    create_virtual_env(user_venv_dir)

    # Save requirements.txt if provided, otherwise create an empty requirements.txt
    requirements_path = os.path.join(user_venv_dir, "requirements.txt")
    if requirements:
        with open(requirements_path, "wb") as f:
            shutil.copyfileobj(requirements.file, f)
    else:
        with open(requirements_path, "w") as f:
            f.write("")

    # Install dependencies
    install_dependencies(user_venv_dir, requirements_path)

    # Install numpy by default unless already in dependencies
    with open(requirements_path, "r") as f:
        requirements_content = f.read()
    
    if "numpy" not in requirements_content:
        pip_path = os.path.join(user_venv_dir, "bin", "pip")
        subprocess.run([pip_path, "install", "numpy"], check=True)

    # Save user script
    script_path = os.path.join(user_upload_dir, "user_script.py")
    with open(script_path, "wb") as buffer:
        shutil.copyfileobj(script.file, buffer)

    # Add script directory to sys.path before importing
    sys.path.insert(0, user_upload_dir)

    # Load the module dynamically
    module_name = f"user_script_{user_id}"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Store callable functions that begin with 'metric_'
    # convert user_id to underscored version



    user_functions[user_id] = {
        name: func for name, func in vars(module).items() if callable(func) and name.startswith("metric_")
    }
    return {"message": "Metrics and dependencies uploaded successfully", "user_id": user_id, "functions": list(user_functions[user_id].keys())}

@app.get("/inspect-uploaded-functions/{user_id}")
async def inspect_uploaded_functions(user_id: str):
    """Inspects the functions uploaded by the user."""
    if user_id not in user_functions:
        raise HTTPException(status_code=404, detail="User ID not found")
    
    return {"user_id": user_id, "functions": list(user_functions[user_id].keys())}



@app.delete("/clear-user-data/{user_id}")
async def clear_user_data(user_id: str):
    """Clears all stored scripts and virtual environments for a user."""
    user_upload_dir = get_user_path(UPLOAD_DIR, user_id)
    user_venv_dir = get_user_path(VENV_DIR, user_id)
    
    shutil.rmtree(user_upload_dir, ignore_errors=True)
    shutil.rmtree(user_venv_dir, ignore_errors=True)
    user_functions.pop(user_id, None)
    
    return {"message": f"Data for user {user_id} cleared successfully"}



# Helper to ensure outputs are JSON-serializable
def ensure_json_serializable(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):  # covers NumPy scalar types
        return obj.item()
    if isinstance(obj, dict):
        return {k: ensure_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [ensure_json_serializable(v) for v in obj]
    # Base types (int, float, str, bool, None) are already JSON serializable
    return obj



@app.post("/compute-metric")
async def compute_metric(data: ComputeUserMetricRequest):
    """
    Executes a user-defined function in an **isolated virtual environment**.

    - Passes parameters via stdin for safety.
    - Converts JSON lists **without NumPy**.
    - Ensures the result is **always JSON-safe**.
    """
    user_id = data.user_id
    function_name = data.function_name
    params = data.params  # Already a Python dict with lists, no NumPy

    user_venv_dir = get_user_path(VENV_DIR, user_id)
    user_upload_dir = get_user_path(UPLOAD_DIR, user_id)
    python_bin = os.path.join(user_venv_dir, "bin", "python")

    if not os.path.exists(python_bin):
        raise HTTPException(status_code=404, detail=f"Virtual environment not found for user {user_id}")

    script_path = os.path.join(user_upload_dir, "user_script.py")
    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail=f"User script not found for user {user_id}")

    params_json = json.dumps(params)  # Serialize params to a JSON string

    # Command to execute the function inside the user's venv
    # THIS HAS TO BE INDENTED AS SUCH TO WORK   
    command = [
        python_bin, "-c",
        f"""
import sys
import json
sys.path.insert(0, '{user_upload_dir}')
from user_script import {function_name} as func

# Read parameters from stdin
params = json.loads(sys.stdin.read())

# Execute function
try:
    result = func(params)

    # Ensure result follows expected format
    if isinstance(result, dict) and all(k in result for k in ["computed_value", "ideal_value", "range"]):
        result["range"] = list(result["range"])  # Ensure range is a list, not a tuple
        print(json.dumps({{"result": result}}))
    else:
        print(json.dumps({{"error": "Invalid return format from user function"}}))

except Exception as e:
    print(json.dumps({{"error": str(e)}}))
"""
    ]

    process = subprocess.run(command, input=params_json, capture_output=True, text=True)

    if process.returncode != 0:
        raise HTTPException(status_code=500, detail=f"User-defined metric execution failed: {process.stderr}")
    
    print(process.stdout)
    return {"result": json.loads(process.stdout.strip())}




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)
