from dataclasses import dataclass

from common.models.common import Job


@dataclass
class RunningJob:
    """Represents a running job in the dispatcher. Is all of Job + our data"""

    job_data: Job
    """Original data associated with the job"""

    user_id: str
    """User ID associated with the job (Job ID) (used as Redis Key)"""

    max_concurrent_batches: int
    """Maximum number of batches to be processed concurrently"""
    currently_running_batches: int
    """Number of batches currently being processed"""
    completed_batches: int
    """Number of batches that have been processed"""
    errored_batches: int
    """Number of batches that have errored"""
