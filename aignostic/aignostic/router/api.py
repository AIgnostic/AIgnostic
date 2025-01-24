from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, HTTPException
import requests
import aignostic.metrics.metrics as metrics_lib


api = APIRouter()


class DatasetRequest(BaseModel):
    datasetURL: HttpUrl
    modelURL: HttpUrl
    metrics: list[str]


@api.post("/evaluate")
async def generate_metrics_from_info(request: DatasetRequest):
    """
    Frontend will post URLs, metrics, etc., as JSON to this endpoint.
    This function validates, processes, and forwards the data to the controller.
    """
    # Extract data from the validated request
    datasetURL = request.datasetURL
    modelURL = request.modelURL
    metrics = request.metrics
    print("evaluating")
    results = await process_data(datasetURL, modelURL, metrics)
    return {"message": "Data successfully received", "results": results}


# Sanity check endpoint
# This for checking time of last deployment
@api.get("/")
def info():
    return {"message": "Pushed at 21/01/2025 07:32"}


async def process_data(datasetURL: HttpUrl, modelURL: HttpUrl, metrics: list[str]):
    """
    Controller function. Takes data from the frontend, received at the endpoint and then:
    - Passes to data endpoint and fetch data
    - Process the data in preparation for passing to the model
    - Pass to the model, and get the predicitons

    Params:
    - datasetURL : API URL of the dataset
    - modelURL : API URL of the dataset
    - metrics: list of metrics that should be applied
    """

    # fetch data from datasetURL
    print("fetching data")

    data: dict = await fetch_data(datasetURL)

    print(f"fetched: {data}")


    # strip the label from the datapoint
    try:
        print("processing data")
        features = data["features"]
        labels = data["labels"]
        group_ids = data["group_ids"]
        predictions = await query_model(modelURL, {"features": features, "labels": labels, "group_ids": group_ids})  
        print(predictions) 
        predicted_labels = predictions["predictions"]

        metrics_results = metrics_lib.calculate_metrics(labels, predicted_labels, metrics)
    except Exception as e:
        print(f"Error while processing data: {e}")
        raise HTTPException(status_code=500, detail=f"Error while processing data: {e}")

    return metrics_results


async def fetch_data(dataURL: HttpUrl) -> dict:
    """
    Helper function to fetch data from the dataset API

    Params:
    - dataURL : API URL of the dataset
    """
    try:
        # Send a GET request to the dataset API
        response = requests.get(dataURL)

        # Check if the request was successful
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Return the data
        return data
    except requests.exceptions.RequestException as e:
        HTTPException(status_code=400, detail=f"Error while fetching data: {e}")
    except Exception as e:
        HTTPException(status_code=500, detail=f"Error while fetching data: {e}")


async def query_model(modelURL: HttpUrl, data: dict):
    """
    Helper function to query the model API

    Params:
    - modelURL : API URL of the model
    """
    try:
        # Send a POST request to the model API
        response = requests.post(url=modelURL, json=data)

        # Check if the request was successful
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Return the data
        return data
    except Exception as e:
        HTTPException(status_code=500, detail=f"Error while querying model: {e}")
