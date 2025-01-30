import requests
from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, HTTPException
from aignostic.pydantic_models.data_models import ModelInput, FetchDatasetRequest
from aignostic.dataset.validate_dataset_api import fetch_dataset
from aignostic.metrics.metrics import calculate_metrics


api = APIRouter()


class EvaluateModelRequest(BaseModel):
    dataset_url: HttpUrl
    dataset_api_key: str
    model_url: HttpUrl
    model_api_key: str
    metrics: list[str]


class EvaluateModelResponse(BaseModel):
    message: str = "Data successfully received"
    results: dict


@api.post("/evaluate")
def generate_metrics_from_info(request: EvaluateModelRequest) -> EvaluateModelResponse:
    """
    Controller function. Takes data from the frontend, received at the endpoint and then:
    - Passes to data endpoint and fetch data
    - Process the data in preparation for passing to the model
    - Pass to the model, and get the predicitons

    Params:
    - request : EvaluateModelRequest - Pydantic model for the request
    """
    fetch_dataset_request = FetchDatasetRequest(**request.model_dump())
    data: ModelInput = fetch_dataset(fetch_dataset_request)

    predictions: dict = query_model(request.model_url, request.model_api_key, data)

    try:
        predicted_labels: list = predictions["predictions"]

        results = calculate_metrics(data.labels, predicted_labels, request.metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while processing data: {e}")

    return EvaluateModelResponse(results=results)


def query_model(modelURL: HttpUrl, modelAPIKey: str, data: ModelInput) -> dict:
    """
    Helper function to query the model API

    Params:
    - modelURL : API URL of the model
    - data : Data to be passed to the model in JSON format with DataSet pydantic model type
    - modelAPIKey : API key for the model
    """
    try:
        headers = {"Authorization": f"Bearer {modelAPIKey}"} if modelAPIKey else {}
        response = requests.post(url=modelURL, json=data.model_dump(), headers=headers)

        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.json()["detail"],
        )

    try:
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not parse model response - {e}; response = {response.text}")
