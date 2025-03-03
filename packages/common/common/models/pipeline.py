"""
Models related to the evaluation of various metrics at different stages in the pipeline.
We define a set of different messages we can pass around.

Terminology:
- MetricCalculationRequest: A request, made by the user, to calculate metrics for a data source and model - it does not
    care how that metric is calculated, just that it is.
- Job: The request from the user to compute metrics for a data source and model, _plus_ concurrency control
    This makes it a more concrete thing our pipeline can work with - it it what tells the start of the pipeline what
    it needs to kick off. In other words it what the overall pipeline works to complete.
- Batch: A single unit of work that is part of a job. A job can be broken down into multiple batches to be processed,
    and a worker will process each Batch

The API send the dispatcher a Job to dispatch, which it then breaks down into Batches to be processed by the workers.
"""

from enum import Enum
from typing import Optional
from pydantic import (
    BaseModel,
    HttpUrl,
)


class MetricCalculationJob(BaseModel):
    """A very basic requests - calculate metrics for this data source & model"""

    data_url: HttpUrl
    """URL of the data source"""

    model_url: HttpUrl
    """URL of the model"""

    data_api_key: str
    """API key for the data source"""

    model_api_key: str
    """API key for the model"""

    metrics: list[str]
    """List of metrics to be calculated"""

    model_type: str
    """Type of model"""


class PipelineJob(BaseModel):
    """Sent to the Dispatcher to start a new job and dispatch the appropriate number of batches"""

    job_id: str
    """Identifier for the job"""

    # Concurrency control
    max_concurrent_batches: int
    """Maximum number of batches to run concurrently"""
    batches: int
    """Total batches to run"""
    batch_size: int
    """Size of each batch"""

    @property
    def total_sample_size(self) -> int:
        """Tell us the total samples needed for this job - batch size * number of batches"""
        return self.batches * self.batch_size

    metrics: MetricCalculationJob
    """Data for the metrics this Job should calculate"""


class JobStatus(str, Enum):
    """Status of a job"""

    COMPLETED = "completed"
    """Job is completed"""
    ERRORED = "errored"
    """Job has errored"""


class JobStatusMessage(BaseModel):
    """Sent to the Dispatcher to indicate that a job has been completed or errored"""

    job_id: str
    """Identifier for the job"""

    batch_id: str
    """Identifier for the batch"""

    status: JobStatus
    """Status of the job"""

    errorMessage: Optional[str] = None
    """Error message if the job has errored"""


class Batch(BaseModel):
    """A batch of a job"""

    job_id: str
    """Identifier (UUID) for the originating job"""

    batch_id: str
    """Identifier (UUID) for the batch"""

    batch_size: int
    """Size of the batch to process"""

    total_sample_size: int
    """Total samples in the batch"""

    metrics: MetricCalculationJob
    """Data for the metrics this Batch should calculate (from the Job)"""
