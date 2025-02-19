from pydantic import BaseModel  # , field_validator
from typing import Optional
# from common.utils import nested_list_to_np

class Job(BaseModel):
    """
    Job pydantic model represents the request body when sending a request
    to calculate metrics. It includes list of metrics to be calculated as well as all relevant
    data for the task

    :param batch_size: int - the size of the batch to be processed
    :param data_url: str - the URL of the dataset to be validated
    :param model_url: str - the URL of the model to be used
    :param data_api_key: str - the API key for the dataset
    :param model_api_key: str - the API key for the model
    """
    batch_size: int
    metrics: list[str]
    data_url: str
    model_url: str
    data_api_key: str
    model_api_key: str


class ModelInput(BaseModel):
    """
    A model for a dataset to be sent to a model

    Attributes:
        features: list[list] - the features of the dataset
        labels: list[list] - the labels of the dataset
        group_id: list[int] - the group IDs for the dataset
    """
    features: list[list]
    labels: list[list]
    group_ids: list[int]

    # @field_validator('features', 'labels', mode='after')
    # def convert_to_np_array(cls, v):
    #     return nested_list_to_np(v)

class ModelResponse(BaseModel):
    """
    A model for a response from a model

    Attributes:
        predictions: list[list] - the predictions from the model
        confidence_scores: Optional[list[list]] - the confidence scores from the model (default is None)
    """
    predictions: list[list]
    confidence_scores: Optional[list[list]] = None
