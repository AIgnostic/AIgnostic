from api.router.rabbitmq import get_channel
from common.models.pipeline import MetricCalculationJob, PipelineJob
from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pika.adapters.blocking_connection import BlockingChannel
from common.rabbitmq.constants import JOB_QUEUE
from metrics.metrics import task_type_to_metric
from metrics.models import MetricsInfo

api = APIRouter()
BATCH_SIZE = 50
NUM_BATCHES = 10
MAX_CONCURRENT_BATCHES = 3
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
    user_id: str


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
        dispatch_job(
            metrics=MetricCalculationJob(
                data_url=request.dataset_url,
                model_url=request.model_url,
                data_api_key=request.dataset_api_key,
                model_api_key=request.model_api_key,
                metrics=request.metrics,
                model_type=request.model_type,
            ),
            batches=NUM_BATCHES,
            batch_size=BATCH_SIZE,
            max_concurrent_batches=MAX_CONCURRENT_BATCHES,
            channel=channel,
            job_id=request.user_id,
        )
        print("Dispatched jobs")
        return JSONResponse({"message": "Created and dispatched jobs"}, status_code=202)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dispatching jobs - {e}")


@api.get("/retrieve-metric-info", response_model=MetricsInfo)
async def retrieve_info() -> MetricsInfo:
    """
    Retrieve information about the types of tasks expected / supported by the library
    as well as all the metrics that can be calculated for each task type.

    :return: MetricsInfo - contains the mapping from task type to metrics
    """
    print("Retrieving metrics info")

    return MetricsInfo(task_to_metric_map=task_type_to_metric)


def dispatch_job(
    metrics: MetricCalculationJob,
    max_concurrent_batches: int,
    batches: int,
    batch_size: int,
    channel: BlockingChannel,
    job_id: str,
):
    job = PipelineJob(
        job_id=job_id,
        max_concurrent_batches=max_concurrent_batches,
        batches=batches,
        batch_size=batch_size,
        metrics=metrics,
    )
    message = job.json()
    channel.basic_publish(
        exchange="", routing_key=JOB_QUEUE, body=message, mandatory=True
    )
    return job_id
