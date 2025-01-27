from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

MOCK_MODEL_API_KEY = "scikit-mock-test-key"
MOCK_DATASET_API_KEY = "dataset-api-key"


def extract_api_key(api_key: str):
    if api_key is not None and api_key.startswith('Bearer '):
        return api_key.split(' ')[1]
    return None


def get_model_api_key(api_key: str = Depends(api_key_header)):
    """
    Check if the API key is valid
    """
    api_key = extract_api_key(api_key)
    if not api_key:
        raise HTTPException(status_code=403, detail="Forbidden Request: API Key not in expected format")
    elif api_key == MOCK_MODEL_API_KEY:
        return api_key
    raise HTTPException(status_code=401, detail=f"Unauthorised Access: Invalid API Key - {api_key}")


def get_dataset_api_key(api_key: str = Depends(api_key_header)):
    """
    Check if the API key is valid
    """
    api_key = extract_api_key(api_key)
    if not api_key:
        raise HTTPException(status_code=403, detail="Forbidden Request: API Key not in expected format")
    elif api_key == MOCK_DATASET_API_KEY:
        return api_key
    raise HTTPException(status_code=401, detail=f"Unauthorised Access: Invalid API Key - {api_key}")
