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

    results = await process_data(datasetURL, modelURL, metrics)
    print("Got results")

    return {"message": "Data successfully received", "results": results}


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
    data: dict = await fetch_data(datasetURL)
    print(data)

    print("Fetched Data")
    # strip the label from the datapoint
    try:
        rows = data["rows"]
        feature, true_label = [rows[0][:-1]], [rows[0][-1]]
        print("Feature:", feature)
    
        print("True Label:", true_label)
        print("Shape of Features:", len(feature))
        print("Shape of Feature:", len(feature[0]))
        print("Shape of TL:", len(true_label))
        print("Split Data")
        prediction = await query_model(modelURL, {"column_names": data["column_names"][:-1],  "rows": feature})
        print("Queried Model")
        print(prediction)
        predicted_labels = [item for sublist in prediction["rows"] for item in sublist]
        print("Processed Data")
        metrics_results = metrics_lib.calculate_metrics(true_label, predicted_labels, metrics)
        print("Calculated Metrics")
        print(metrics_results)
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
        # Send a POST request to the dataset API
        response = requests.post(url=modelURL, json=data)

        # Check if the request was successful
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Return the data
        return data
    except Exception as e:
        print(f"Error while querying model: {e}")
        HTTPException(status_code=500, detail=f"Error while querying model: {e}")
