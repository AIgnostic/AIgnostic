'''
This file contains the script that a worker runs to process jobs on the job queue
Each worker:
- Fetches a job (containing a batch size and a list of metrics to compute)
- Fetches the data from the data URL
- Fetches the model from the model URL
- Computes the metrics
- Puts the results on a results queue
''' 

import requests
from fastapi import HTTPException
from pydantic.networks import HttpUrl
from aignostic.metrics import metrics as metrics_lib
from aignostic.router.connection_constants import channel, JOB_QUEUE
from aignostic.pydantic_models.job import Job
import json
from typing import Optional

def fetch_job() -> Optional[Job]:
    """
    Function to fetch a job from the job queue
    """
    method_frame, header_frame, body = channel.basic_get(queue=JOB_QUEUE)
    if method_frame:
        job_data = json.loads(body)
        try:
            return Job(**job_data)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid job format: {e}")
    return None

def process_job(job: Job):


    # fetch data from datasetURL
    data: dict = await fetch_data(job.data_url, job.data_api_key)

    # strip the label from the datapoint
    try:
        features = data["features"]
        labels = data["labels"]
        group_ids = data["group_ids"]
    except KeyError:
        raise HTTPException(status_code=500, detail="KeyError occurred during data processing")
    except Exception:
        raise HTTPException(status_code=500, detail="Error while processing data")

    # TODO: Separate model input and dataset output so labels and group IDs are not passed to the model

    predictions = await query_model(
        job.model_url,
        {
            "features": features,
            "labels": labels,
            "group_ids": group_ids
        },
        job.model_api_key
    )

    try:
        predicted_labels = predictions["predictions"]
        metrics_results = metrics_lib.calculate_metrics(labels, predicted_labels, job.metrics)
        return metrics_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while processing data: {e}")




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


async def fetch_data(data_url: HttpUrl, dataset_api_key) -> dict:
    """
    Helper function to fetch data from the dataset API

    Params:
    - dataURL : API URL of the dataset
    """
    # Send a GET request to the dataset API
    if dataset_api_key is None:
        response = requests.get(data_url)
    else:
        response = requests.get(data_url, headers={"Authorization": f"Bearer {dataset_api_key}"})

    try:
        # Raise errpr if the request was not successful
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise HTTPException(status_code=response.status_code, detail=response.json()["detail"])

    try:
        # Parse the response JSON
        data = response.json()

        # Return the data
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while fetching data: {e}")


if __name__ == "__main__":
    while True:
        job = fetch_job()
        if job:
            job = json.loads(job)
            process_job(job)

        