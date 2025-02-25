from api.router.rabbitmq import get_channel
from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, Depends, HTTPException
import json
from fastapi.responses import JSONResponse
from pika.adapters.blocking_connection import BlockingChannel
from common.rabbitmq.constants import JOB_QUEUE


api = APIRouter()
BATCH_SIZE = 50
NUM_BATCHES = 1
# total sample size should be a multiple of batch size
# TOTAL_SAMPLE_SIZE = round(1000 / BATCH_SIZE) * BATCH_SIZE
TOTAL_SAMPLE_SIZE = BATCH_SIZE * NUM_BATCHES


class ModelEvaluationRequest(BaseModel):
    dataset_url: HttpUrl
    dataset_api_key: str
    model_url: HttpUrl
    model_api_key: str
    metrics: list[str]
    model_type: str


@api.post("/evaluate")
async def generate_metrics_from_info(
    request: ModelEvaluationRequest, channel=Depends(get_channel)
):
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

        for i in range(TOTAL_SAMPLE_SIZE // BATCH_SIZE):
            dispatch_job(
                batch_size=BATCH_SIZE,
                total_sample_size=TOTAL_SAMPLE_SIZE,
                metrics=request.metrics,
                model_type=request.model_type,
                data_url=request.dataset_url,
                model_url=request.model_url,
                data_api_key=request.dataset_api_key,
                model_api_key=request.model_api_key,
                channel=channel,
            )
            print(f"Dispatched job {i+1}")
        return JSONResponse(
            {"message": "Created and dispatched jobs"}, status_code=202
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dispatching jobs - {e}")


def dispatch_job(
    batch_size: int,
    total_sample_size: int,
    metrics: list[str],
    model_type: str,
    data_url: HttpUrl,
    model_url: HttpUrl,
    data_api_key: str,
    model_api_key: str,
    channel: BlockingChannel,
):
    """
    Function to dispatch a job to the model
    """
    job_json = {
        "batch_size": batch_size,
        "total_sample_size": total_sample_size,
        "metrics": metrics,
        "model_type": model_type,
        "data_url": str(data_url),
        "model_url": str(model_url),
        "data_api_key": data_api_key,
        "model_api_key": model_api_key,
    }
    message = json.dumps(job_json)
    channel.basic_publish(exchange="", routing_key=JOB_QUEUE, body=message)
