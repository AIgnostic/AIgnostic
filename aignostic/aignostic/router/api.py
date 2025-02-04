from pydantic import BaseModel, HttpUrl
<<<<<<< HEAD
from fastapi import HTTPException
import json
from aignostic.router.connection_constants import channel
=======
from fastapi import APIRouter, HTTPException
import requests
import aignostic.metrics.metrics as metrics_lib
import pika 
import json


RABBIT_MQ_HOST = 'localhost'

api = APIRouter()
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_MQ_HOST))
channel = connection.channel()
channel.queue_declare(queue='job_queue')

>>>>>>> a7a014e7e935043ab0b4bce71f0a140fa8eb07b3

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
    results = await process_data(request)

    return {
        "message": "Data successfully received",
        "results": results,
    }


# Sanity check endpoint
# This for checking time of last deployment
@api.get("/")
def info():
    return {"message": "Pushed at 21/01/2025 07:32"}


async def process_data(request: DatasetRequest):
    """
    Controller function. Takes data from the frontend, received at the endpoint and then:
    - Dispatches jobs to job_queue
    - Workers will handle the jobs and return the results
    Params:
    - datasetURL : API URL of the dataset
    - modelURL : API URL of the model
    - metrics: list of metrics that should be applied
    """
<<<<<<< HEAD

    # Dispatch job to the model
    try :
        dispatch_job(10, request.metrics)

=======

    # Dispatch job to the model
    try :

        dispatch_job(10, request.metrics)

    # TODO: Move this logic to workers
    # fetch data from datasetURL
    # data: dict = await fetch_data(request.data_url, request.data_api_key)

    # # strip the label from the datapoint
    # try:
    #     features = data["features"]
    #     labels = data["labels"]
    #     group_ids = data["group_ids"]
    # except KeyError:
    #     raise HTTPException(status_code=500, detail="KeyError occurred during data processing")
    # except Exception:
    #     raise HTTPException(status_code=500, detail="Error while processing data")

    # # TODO: Separate model input and dataset output so labels and group IDs are not passed to the model

    # # predictions = await query_model(
    #     request.model_url,
    #     {
    #         "features": features,
    #         "labels": labels,
    #         "group_ids": group_ids
    #     },
    #     request.model_api_key
    # )

    # try:
    #     predicted_labels = predictions["predictions"]
    #     metrics_results = metrics_lib.calculate_metrics(labels, predicted_labels, request.metrics)
>>>>>>> a7a014e7e935043ab0b4bce71f0a140fa8eb07b3
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dispatching jobs - {e}")

<<<<<<< HEAD
def dispatch_job(batch_size: int, metric: list[str], data_url, model_url, data_api_key: str, model_api_key: str):
=======
    metrics_results = "LOLLLL"

    return metrics_results


async def fetch_data(data_url: HttpUrl, dataset_api_key) -> dict:
>>>>>>> a7a014e7e935043ab0b4bce71f0a140fa8eb07b3
    """
    Function to dispatch a job to the model
    """
    job_json = {
        "batch_size": batch_size,
        "metric": metric,
        "data_url": data_url,
        "model_url": model_url,
        "data_api_key": data_api_key,
        "model_api_key": model_api_key
    }
    message = json.dumps(job_json)
    channel.basic_publish(exchange='', routing_key='job_queue', body=message)


<<<<<<< HEAD
=======
async def query_model(model_url: HttpUrl, data: dict, model_api_key):
    """
    Helper function to query the model API

    Params:
    - modelURL : API URL of the model
    - data : Data to be passed to the model in JSON format with DataSet pydantic model type
    - modelAPIKey : API key for the model
    """
    # Send a POST request to the model API
    if model_api_key is None:
        response = requests.post(url=model_url, json=data)
    else:
        response = requests.post(url=model_url, json=data, headers={"Authorization": f"Bearer {model_api_key}"})

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise HTTPException(detail=e.response.json()["detail"], status_code=e.response.status_code)

    check_model_response(response, data["labels"])

    try:
        # Check if the request was successful

        # Parse the response JSON
        data = response.json()

        # Return the data
        return data
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

    return


def dispatch_job(batch_size: int, metric: list[str]):
    """
    Function to dispatch a job to the model
    """
    job_json = {
        "batch_size": batch_size,
        "metric": metric
    }
    message = json.dumps(job_json)
    channel.basic_publish(exchange='', routing_key='job_queue', body=message)


>>>>>>> a7a014e7e935043ab0b4bce71f0a140fa8eb07b3
