from pydantic import BaseModel  # , field_validator
from typing import Optional

# from common.utils import nested_list_to_np


class Job(BaseModel):  # pragma: no cover
    """
    Job pydantic model represents the request body when sending a request
    to calculate metrics. It includes list of metrics to be calculated as well as all relevant
    data for the task

    :param max_concurrenct_batches: int - the maximum number of batches to be processed concurrently

    :param batch_size: int - the size of the batch to be processed
    :param total_sample_size: int - the total number of samples used metric evaluation
    :param metrics: list[str] - the metrics to be calculated
    :param model_type: str - the type of the model
    :param data_url: str - the URL of the dataset to be validated
    :param model_url: str - the URL of the model to be used
    :param data_api_key: str - the API key for the dataset
    :param model_api_key: str - the API key for the model
    """

    max_concurrenct_batches: int

    batch_size: int
    total_sample_size: int
    metrics: list[str]
    model_type: str
    data_url: str
    model_url: str
    data_api_key: str
    model_api_key: str
    user_id: str


class ModelInput(BaseModel):  # pragma: no cover
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


class ModelResponse(BaseModel):  # pragma: no cover
    """
    A model for a response from a model

    Attributes:
        predictions: list[list] - the predictions from the model
        confidence_scores: Optional[list[list]] - the confidence scores from the model (default is None)
    """

    predictions: list[list]
    confidence_scores: Optional[list[list]] = None


class LLMInput(ModelInput, BaseModel):
    """
    A model for next token generation

    Attributes:
        prompt: str - the prompt for the language model
        max_length: int - the maximum length of the generated sequence
    """

    prompt: str
    max_length: int


class LLMResponse(ModelInput, BaseModel):
    """
    A model for next token generation

    Attributes:
        response: str - response generated from the model
    """

    response: str
