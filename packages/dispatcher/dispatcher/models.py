from common.models.pipeline import PipelineJob
from pydantic import BaseModel


class RunningJob(BaseModel):
    """Represents a running job in the dispatcher. Is all of Job + our data"""

    job_data: PipelineJob
    """Original data associated with the job"""

    currently_running_batches: int
    """Number of batches currently being processed"""
    completed_batches: int
    """Number of batches that have been processed"""
    errored_batches: int
    """Number of batches that have errored"""
    pending_batches: int
    """Number of batches that are pending"""
