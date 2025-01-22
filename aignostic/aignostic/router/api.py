from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, HTTPException
import requests
import aignostic.metrics.metrics as metricsLib


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
    try:
        # Extract data from the validated request
        datasetURL = request.datasetURL
        modelURL = request.modelURL
        metrics = request.metrics

        results = await process_data(datasetURL, modelURL, metrics)

        return {"message": "Data successfully received", "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

    try:
        # fetch data from datasetURL
        data = await fetch_data(datasetURL)

        # strip the label from the datapoint
        feature, trueLabel = [data[0][:-1]], [data[0][-1]]

        # pass data to modelURL and return predictions
        prediction = await query_model(modelURL, {"column_names": None, "rows": feature})
        predictedLabels = [item for sublist in prediction["rows"] for item in sublist]

        metricsResults = metricsLib.calculate_metrics(trueLabel, predictedLabels, metrics)
        
        return metricsResults
    except Exception as e:
        print("Error while processing data:", e)
        return None


async def fetch_data(dataURL: HttpUrl):
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
    except Exception as e:
        print("Error while fetching data:", e)
        return None


async def query_model(modelURL: HttpUrl, data: dict):
    """
    Helper function to query the model API

    Params:
    - modelURL : API URL of the model
    """
    try:
        # Send a POST request to the dataset API
        response = requests.post(url=modelURL, json=data)

        # Check if the request was successful
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Return the data
        return data
    except Exception as e:
        print("Error while fetching data:", e)
        return None
