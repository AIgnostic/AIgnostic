from abc import ABC
from enum import Enum

from metrics.models import WorkerResults
from pydantic import BaseModel  # , field_validator
from typing import Any, Optional, Union


class DatasetResponse(BaseModel):  # pragma: no cover
    """
    A model for a dataset to be sent to a model

    Attributes:
        features: list[list] - the features of the dataset
        labels: list[list] - the labels of the dataset
        group_id: list[int] - the group IDs for the dataset
    """

    features: list[list]
    labels: list[list]
    group_ids: Optional[list[int]]

    # @field_validator('features', 'labels', mode='after')
    # def convert_to_np_array(cls, v):
    #     return nested_list_to_np(v)


class ModelResponse(BaseModel):  # pragma: no cover
    """
    A model for a response from a model

    Attributes:
        predictions: list[list] - the predictions from the model
        confidence_scores: Optional[list[list]] - the confidence scores from the model (default is None)
    """

    predictions: list[list]
    confidence_scores: Optional[list[list]] = None


class LLMInput(DatasetResponse, BaseModel):  # pragma: no cover
    """
    A model for next token generation

    Attributes:
        prompt: str - the prompt for the language model
        max_length: int - the maximum length of the generated sequence
    """

    prompt: str
    max_length: int


class LLMResponse(DatasetResponse, BaseModel):  # pragma: no cover
    """
    A model for next token generation

    Attributes:
        response: str - response generated from the model
    """

    response: str


class AggregatorMessage(BaseModel, ABC):  # pragma: no cover
    """
    Model for messages sent by the aggregator to the frontend
    Params:
    messageType: str - the type of the message (e.g. LOG)
    message: str - the message to be displayed
    statusCode: int - the status code of the message
    content: Any - the additional content (e.g. the report for a REPORT type)
    """

    messageType: str
    message: str
    statusCode: int
    content: Any

    class Config:
        arbitrary_types_allowed = True


class MessageType(str, Enum):  # pragma: no cover
    LOG = "LOG"
    ERROR = "ERROR"
    METRICS_INTERMEDIATE = "METRICS_INTERMEDIATE"
    METRICS_COMPLETE = "METRICS_COMPLETE"
    REPORT = "REPORT"


class JobType(str, Enum):
    RESULT = "RESULT"
    ERROR = "ERROR"


class WorkerError(BaseModel):  # pragma: no cover
    """
    WorkerError pydantic model represents the structure of the errors found on the results queue
    i.e. what worker sends to the queue
    and what aggregator picks up from the queue
    """

    error_message: str
    error_code: int


class AggregatorJob(BaseModel):  # pragma: no cover
    """
    AggregatorJob pydantic model represents the structure of the jobs found on the results queue
    i.e. what worker sends to the queue
    and what aggregator picks up from the queue
    """

    job_type: JobType
    content: Union[WorkerResults, WorkerError]


class ComputeUserMetricRequest(BaseModel):  # pragma: no cover
    user_id: str
    function_name: str
    params: dict
