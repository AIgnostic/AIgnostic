from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, HTTPException
import json
from aignostic.router.connection_constants import channel
from fastapi.responses import JSONResponse


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
    Controller function. Takes data from the frontend, received at the endpoint and then:
    - Dispatches jobs to job_queue
    - Workers will handle the jobs and return the results
    Params:
    - datasetURL : API URL of the dataset
    - modelURL : API URL of the model
    - metrics: list of metrics that should be applied
    """
    try:
        dispatch_job(batch_size=10,
                     metric=request.metrics,
                     data_url=request.data_url,
                     model_url=request.model_url,
                     data_api_key=request.data_api_key,
                     model_api_key=request.model_api_key)
        return JSONResponse({"message": "Creating and dispatching jobs"}, status_code=202)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dispatching jobs - {e}")


# Sanity check endpoint
# This for checking time of last deployment
@api.get("/")
def info():
    return {"message": "Pushed at 21/01/2025 07:32"}


def dispatch_job(batch_size: int,
                 metric: list[str],
                 data_url: HttpUrl,
                 model_url: HttpUrl,
                 data_api_key: str,
                 model_api_key: str):
    """
    Function to dispatch a job to the model
    """
    job_json = {
        "batch_size": batch_size,
        "metrics": metric,
        "data_url": str(data_url),
        "model_url": str(model_url),
        "data_api_key": data_api_key,
        "model_api_key": model_api_key
    }
    message = json.dumps(job_json)
    channel.basic_publish(exchange='', routing_key='job_queue', body=message)
