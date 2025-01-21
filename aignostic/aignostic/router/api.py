from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, HTTPException
import requests

api = APIRouter()


class DatasetRequest(BaseModel):
    datasetURL: HttpUrl
    modelURL: HttpUrl
    metrics: list[str]


@api.post("/get_info")
async def get_info(request: DatasetRequest):
    """
    Frontend will post URLs, metrics, etc., as JSON to this endpoint.
    This function validates, processes, and forwards the data to the controller.
    """
    try:
        # Extract data from the validated request
        datasetURL = request.datasetURL
        modelURL = request.modelURL
        metrics = request.metrics

        print("Received request: ", datasetURL, modelURL, metrics)

        await processData(datasetURL, modelURL, metrics)

        print("YAY")

        # # Example of processing or passing data to a controller
        # # Here you could make a request to the dataset API or perform metric calculations
        # result = {
        #     "api_url": api_url,
        #     "processed_metrics": [metric.upper() for metric in metrics],  # Example processing
        # }

        # return {"message": "Data successfully processed", "result": result}

        return {"message": "Data successfully received"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api.get("/")
def hello():
    return {"message": "Pushed at 21/01/2025 07:32"}


@api.get("/repeat/{text}")  # /repeat/hello, /repeat/a,
def repeat(text: str):
    return {"message": text}


class Request(BaseModel):  # class Request extends BaseModel
    text: str


@api.post("/echo")
def echo(request: Request):
    return {"message": request.text}


async def processData(datasetURL: HttpUrl, modelURL: HttpUrl, metrics: list[str]):
    # fetch data from datasetURL
    data = await fetch_data(datasetURL)

    print("Data fetched.")

    # pass data to modelURL and return predictions
    prediction = await query_model(modelURL, data)

    print("Prediction received.")

    # calculate metrics


async def fetch_data(dataURL: HttpUrl):
    try:
        # Send a GET request to the dataset API
        response = requests.get(dataURL)

        # Check if the request was successful
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Print or return the data
        print("Data retrieved:", data)
        return data
    except requests.exceptions.RequestException as e:
        print("Error while fetching data:", e)
        return None
    

async def query_model(modelURL: HttpUrl, data: dict):
    try:
        print(modelURL)

        # Send a POST request to the dataset API
        response = requests.get(modelURL)
        print("getted " + response)
        response = requests.post(modelURL, json={"column_names": None, "rows": data.toList()})
        print("posted " + response)

        # Check if the request was successful
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Print or return the data
        print("Data retrieved:", data)
        return data
    except requests.exceptions.RequestException as e:
        print("Error while fetching data:", e)
        return None
