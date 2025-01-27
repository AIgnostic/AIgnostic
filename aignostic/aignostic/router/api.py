from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, HTTPException
import requests
import aignostic.metrics.metrics as metrics_lib


api = APIRouter()


class DatasetRequest(BaseModel):
    data_url: HttpUrl
    model_url: HttpUrl
    model_api_key: str
    data_api_key: str
    metrics: list[str]


@api.post("/evaluate")
async def generate_metrics_from_info(request: DatasetRequest):
    """
    Frontend will post URLs, metrics, etc., as JSON to this endpoint.
    This function validates, processes, and forwards the data to the controller.
    """
    # Extract data from the validated request
    data_url = request.data_url
    model_url = request.model_url
    data_api_key = request.data_api_key
    model_api_key = request.model_api_key
    metrics = request.metrics

    results = await process_data(data_url, model_url, metrics, data_api_key, model_api_key)

    return {"message": "Data successfully received", "results": results}


# Sanity check endpoint
# This for checking time of last deployment
@api.get("/")
def info():
    return {"message": "Pushed at 21/01/2025 07:32"}


async def process_data(datasetURL: HttpUrl, modelURL: HttpUrl, metrics: list[str], datasetAPIKey, modelAPIKey):
    """
    Controller function. Takes data from the frontend, received at the endpoint and then:
    - Passes to data endpoint and fetch data
    - Process the data in preparation for passing to the model
    - Pass to the model, and get the predicitons

    Params:
    - datasetURL : API URL of the dataset
    - modelURL : API URL of the model
    - metrics: list of metrics that should be applied
    """
    # fetch data from datasetURL
    data: dict = await fetch_data(datasetURL, datasetAPIKey)

    # strip the label from the datapoint
    try:
        features = data["features"]
        labels = data["labels"]
        group_ids = data["group_ids"]
        predictions = await query_model(
            modelURL,
            {
                "features": features,
                "labels": labels,
                "group_ids": group_ids
            },
            modelAPIKey
        )
        predicted_labels = predictions["predictions"]
        metrics_results = metrics_lib.calculate_metrics(labels, predicted_labels, metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while processing data: {e}")

    return metrics_results


async def fetch_data(dataURL: HttpUrl, datasetAPIKey) -> dict:
    """
    Helper function to fetch data from the dataset API

    Params:
    - dataURL : API URL of the dataset
    """
    try:
        # Send a GET request to the dataset API
        if datasetAPIKey is None:
            response = requests.get(dataURL)
        else:
            response = requests.get(dataURL, headers={"Authorization": f"Bearer {datasetAPIKey}"})

        # Check if the request was successful
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Return the data
        return data
    except requests.exceptions.RequestException as e:
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized access: Please check your API Key")
        raise HTTPException(status_code=400, detail=f"Error while fetching data: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while fetching data: {e}")


async def query_model(modelURL: HttpUrl, data: dict, modelAPIKey):
    """
    Helper function to query the model API

    Params:
    - modelURL : API URL of the model
    - data : Data to be passed to the model in JSON format with DataSet pydantic model type
    - modelAPIKey : API key for the model
    """
    try:
        # Send a POST request to the dataset API
        # TODO: Verify whether this should be get or post request
        if modelAPIKey is None:
            response = requests.post(url=modelURL, json=data)
        else:
            response = requests.post(url=modelURL, json=data, headers={"Authorization": f"Bearer {modelAPIKey}"})

        # Check if the request was successful
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Return the data
        return data

    except requests.exceptions.RequestException as e:
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized access: Please check your API Key")
        raise HTTPException(status_code=400, detail=f"Error while fetching data: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while querying model: {e}")
