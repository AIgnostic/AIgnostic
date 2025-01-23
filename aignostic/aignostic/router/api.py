from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, HTTPException
import requests
import aignostic.metrics.metrics as metrics_lib


api = APIRouter()


class DatasetRequest(BaseModel):
    datasetURL: HttpUrl
    modelURL: HttpUrl
    modelAPIKey: str
    datasetAPIKey: str
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
    datasetAPIKey = request.datasetAPIKey
    modelAPIKey = request.modelAPIKey
    metrics = request.metrics
    results = await process_data(datasetURL, modelURL, metrics, datasetAPIKey=datasetAPIKey, modelAPIKey=modelAPIKey)
    return {"message": "Data successfully received", "results": results}


@api.get("/")
def info():
    return {"message": "Pushed at 21/01/2025 07:32"}


async def process_data(datasetURL: HttpUrl, modelURL: HttpUrl, metrics: list[str],
                       datasetAPIKey=None, modelAPIKey=None):
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
    data: dict = await fetch_data(datasetURL, datasetAPIKey=datasetAPIKey)
    print(data)

    print("Fetched Data")
    # strip the label from the datapoint
    try:
        rows = data["rows"]
        feature, true_label = [rows[0][:-1]], [rows[0][-1]]
        prediction = await query_model(modelURL, {
            "column_names": data["column_names"][:-1],
            "rows": feature},
            modelAPIKey=modelAPIKey
        )
        predicted_labels = [item for sublist in prediction["rows"] for item in sublist]
        metrics_results = metrics_lib.calculate_metrics(true_label, predicted_labels, metrics)
    except Exception as e:
        print(f"Error while processing data: {e}")
        raise HTTPException(status_code=500, detail=f"Error while processing data: {e}")

    return metrics_results


async def fetch_data(dataURL: HttpUrl, datasetAPIKey=None) -> dict:
    """
    Helper function to fetch data from the dataset API

    Params:
    - dataURL : API URL of the dataset
    """
    try:
        # Send a GET request to the dataset API
        response = requests.get(dataURL, headers={"Authorization": f"Bearer {datasetAPIKey}"})

        # Check if the request was successful
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Return the data
        return data
    except requests.exceptions.RequestException as e:
        print(response.headers)
        print(response.text)
        print(response.url)
        print(response._content)
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized access: Please check your API Key")
        raise HTTPException(status_code=400, detail=f"Error while fetching data: {e}")
    except Exception as e:
        print(response.headers)
        print(response.text)
        print(response.url)
        print(response._content)
        HTTPException(status_code=500, detail=f"Error while fetching data: {e}")


async def query_model(modelURL: HttpUrl, data: dict, modelAPIKey=None):
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
        response = requests.post(url=modelURL, json=data, headers={"Authorization": f"Bearer {modelAPIKey}"})

        # Check if the request was successful
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Return the data
        return data
    except Exception as e:
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized access: Please check your API Key")
        print(f"Error while querying model: {e}")
        HTTPException(status_code=500, detail=f"Error while querying model: {e}")
