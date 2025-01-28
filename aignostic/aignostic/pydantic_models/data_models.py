from pydantic import BaseModel
from typing import List


# TODO: Implement in validate_dataset_api.py endpoint
class ValidateDatasetRequest(BaseModel):
    """
    A model for a dataset to be validated

    Attributes:
        url: str - the URL of the dataset to be validated
    """
    url: str


class ModelInput(BaseModel):
    """
    A model for a dataset to be sent over HTTP by JSON

    Attributes:
        features: List[List] - the features of the dataset
        labels: List[List] - the labels of the dataset
        group_id: List[int] - the group IDs for the dataset
    """
    features: List[List]
    labels: List[List]
    group_ids: List[int]


class ModelResponse(BaseModel):
    """
    A model for a response from a model

    Attributes:
        predictions: List[List] - the predictions from the model
    """
    predictions: List[List]
