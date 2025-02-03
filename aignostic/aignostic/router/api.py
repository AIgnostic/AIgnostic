import requests
from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, HTTPException
from aignostic.pydantic_models.data_models import ModelInput, FetchDatasetRequest
from aignostic.pydantic_models.metric_models import CalculateRequest
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
    results: list[dict]


@api.post("/evaluate")
async def generate_metrics_from_info(request: EvaluateModelRequest) -> EvaluateModelResponse:
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
        req = CalculateRequest(
            metrics=request.metrics,
            true_labels=data.labels,
            predicted_labels=predicted_labels
        )
        metrics_map = await calculate_metrics(req)
        results = []
        for metric, value in metrics_map:
            results.append(
                {
                    "metric": metric,
                    "result": value,
                    "legislation_results": ["Legislation placeholder for metric: " + metric],
                    "llm_model_summary": ["LLM holder for metric: " + metric]
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while processing data: {e}")

    return EvaluateModelResponse(results=results)


def query_model(model_url: HttpUrl, model_api_key: str, data: ModelInput) -> dict:
    """
    Helper function to query the model API

    Params:
    - modelURL : API URL of the model
    - data : Data to be passed to the model in JSON format with DataSet pydantic model type
    - modelAPIKey : API key for the model
    """
    headers = {"Authorization": f"Bearer {model_api_key}"} if model_api_key else {}

    try:
        response = requests.post(url=model_url, json=data.model_dump(), headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.json()["detail"],
        )

    check_model_response(response, data.labels)

    try:
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not parse model response - {e}; response = {response.text}")


# TODO: Write a doc explaining error messages and what checking is/isn't supported
def check_model_response(response, labels):
    """
    PRE: response is received from a deserialised pydantic model and labels and types
    have been enforced according to ModelOutput.
    ASSUME: Labels are always correct / have already been validated previously

    Helper function to check the response from the model API and ensure validity compared to data

    Checks are ordered in terms of complexity and computational cost, with the most
    computationally expensive towards the end.

    Params:
    - response : Response object from the model API
    """
    predictions = response.json()["predictions"]
    if len(predictions) != len(labels):
        raise HTTPException(
            detail="Number of model outputs does not match expected number of labels",
            status_code=400
        )

    if len(labels) >= 0:
        if len(predictions[0]) != len(labels[0]):
            raise HTTPException(
                detail="Number of attributes predicted by model does not match number of target attributes",
                status_code=400
            )

        for col_index in range(len(labels[0])):
            if not isinstance(predictions[0][col_index], type(labels[0][col_index])):
                raise HTTPException(
                    detail="Model output type does not match target attribute type",
                    status_code=400
                )
    """
    TODO: Evaluate if this check is necessary -> O(n) complexity where n is number
    of datapoints.
    (As opposed to O(1) complexity or O(d) complexity for above checks)
    """
    num_attributes = len(labels[0])
    for row in predictions[1:]:
        if len(row) != num_attributes:
            raise HTTPException(
                detail="Inconsistent number of attributes for each datapoint predicted by model",
                status_code=400
            )

    """
    TODO: Evaluate if this check is necessary -> O(n*d) complexity where n is number
    of datapoints in batch and d is number of attributes being predicted.
    (As opposed to O(1) complexity or O(d) complexity for above checks)
    """
    for col_index in range(len(predictions[0])):
        col_type = type(labels[0][col_index])
        for row_index in range(len(predictions)):
            if not isinstance(predictions[row_index][col_index], col_type):
                raise HTTPException(
                    detail="All columns for an output label should be of the same type",
                    status_code=400
                )
