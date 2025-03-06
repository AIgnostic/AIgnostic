"""Models related to the dispatcher. We define a set of different messages the dispatcher can receive"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, root_validator


class MetricCalculationJob(BaseModel):
    """A very basic requests - calculate metrics for this data source & model"""

    data_url: str
    """URL of the data source"""

    model_url: str
    """URL of the model"""

    data_api_key: str
    """API key for the data source"""

    model_api_key: str
    """API key for the model"""


class Batch(BaseModel):
    """A batch of a job"""

    user_id: str
    """Identifier for the job"""

    batch_id: str
    """Identifier for the batch"""

    data_url: str
    """URL of the data source"""

    model_url: str
    """URL of the model"""

    data_api_key: str


class PipelineJob(BaseModel):
    """Sent to the Dispatcher to start a new job and dispatch the appropriate number of batches"""

    user_id: str
    """Identifier for the job"""

    # Concurrency control
    # TODO: Better Type Hierachy
    max_concurrent_batches: int
    """Maximum number of batches to run concurrently"""
    batches: int
    """Total batches to run"""

    job_data: MetricCalculationJob
    """Data for the job"""


class JobStatus(str, Enum):
    """Status of a job"""

    COMPLETED = "completed"
    """Job is completed"""
    ERRORED = "errored"
    """Job has errored"""


class JobCompleteMessage(BaseModel):
    """Sent to the Dispatcher to indicate that a job has been completed or errored"""

    user_id: str
    """Identifier for the job"""

    batch_id: str
    """Identifier for the batch"""

    status: JobStatus
    """Status of the job"""

    errorMessage: Optional[str] = None
    """Error message if the job has errored"""

    @root_validator
    def check_error_message(cls, values):
        # By Copilot
        status, errorMessage = values.get("status"), values.get("errorMessage")
        if status == JobStatus.ERRORED and not errorMessage:
            raise ValueError("errorMessage must be provided if status is ERRORED")
        return values
