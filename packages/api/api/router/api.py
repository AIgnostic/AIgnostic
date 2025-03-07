from api.router.rabbitmq import get_jobs_publisher
from common.models.pipeline import MetricCalculationJob, PipelineJob
from common.rabbitmq.publisher import Publisher
from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from metrics.metrics import task_type_to_metric
from metrics.models import MetricsInfo
from common.models.pipeline import (
    MetricCalculationJob,
    PipelineJob,
    JobFromAPI,
    PipelineJobType,
    PipelineHalt,
)

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
    batch_size: int = BATCH_SIZE
    num_batches: int = NUM_BATCHES
    max_conc_batches: int = MAX_CONCURRENT_BATCHES

class StopJobRequest(BaseModel):
    job_id: str


@api.get("/")
async def read_root():
    return {"message": "Welcome to the model evaluation server!"}


@api.post("/evaluate")
async def generate_metrics_from_info(
    request: ModelEvaluationRequest, publisher=Depends(get_jobs_publisher)
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
            batches=request.num_batches,
            batch_size=request.batch_size,
            max_concurrent_batches=request.max_conc_batches,
            publisher=publisher,
            job_id=request.user_id,
        )
        print("Dispatched jobs")
        return JSONResponse({"message": "Created and dispatched jobs"}, status_code=202)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dispatching jobs - {e}")


@api.post("/stop-job")
async def stop_job(request: StopJobRequest, publisher=Depends(get_jobs_publisher)):
    """
    Stop a job with the given job_id
    """
    try:
        message = JobFromAPI(
            job_type=PipelineJobType.HALT_JOB, job=PipelineHalt(job_id=request.job_id)
        ).model_dump_json()
        _ = publisher.publish(message)
        return JSONResponse({"message": "Job stopped"}, status_code=202)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during handling of request to /stop-job - {e}")


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
    publisher: Publisher,
    job_id: str,
):
    job = JobFromAPI(
        job_type=PipelineJobType.START_JOB,
        job=PipelineJob(
            job_id=job_id,
            max_concurrent_batches=max_concurrent_batches,
            batches=batches,
            batch_size=batch_size,
            metrics=metrics,
        )
    )
    
    
    message = job.model_dump_json()

    _ = publisher.publish(message)

    return job_id
