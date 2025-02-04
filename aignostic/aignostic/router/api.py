from pydantic import BaseModel, HttpUrl
from fastapi import HTTPException, FastAPI
from aignostic.router.connection_constants import channel, JOB_QUEUE
from aignostic.pydantic_models.job import Job


class ClientRequest(BaseModel):
    data_url: HttpUrl
    model_url: HttpUrl
    model_api_key: str
    data_api_key: str
    metrics: list[str]


api = FastAPI()  # is this defined alr??

BATCH_SIZE = 10


@api.post("/evaluate")
async def generate_metrics_from_info(request: ClientRequest):
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


async def process_data(request: ClientRequest):
    """
    Controller function. Takes data from the frontend, received at the endpoint and then:
    - Dispatches jobs to job_queue
    - Workers will handle the jobs and return the results
    Params:
    - datasetURL : API URL of the dataset
    - modelURL : API URL of the model
    - metrics: list of metrics that should be applied
    """

    # Dispatch job to the model
    try:
        dispatch_job(batch_size=BATCH_SIZE,
                     metrics=request.metrics,
                     data_url=request.data_url,
                     model_url=request.model_url,
                     data_api_key=request.data_api_key,
                     model_api_key=request.model_api_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dispatching jobs - {e}")


def dispatch_job(batch_size: int, metrics: list[str], data_url: str, model_url: str,
                 data_api_key: str, model_api_key: str):
    """
    Function to dispatch a job to the model queue using the Job schema
    """
    try:
        # Create a JobModel instance for validation and serialization
        job = Job(
            batch_size=batch_size,
            metrics=metrics,
            data_url=data_url,
            model_url=model_url,
            data_api_key=data_api_key,
            model_api_key=model_api_key
        )

        # Serialize the validated job object to JSON
        message = job.model_dump_json()

        # Publish the job message to the queue
        channel.basic_publish(exchange='', routing_key=JOB_QUEUE, body=message)
        print("Job successfully dispatched.")

    except ValueError as e:
        print(f"Error creating job: {e}")
