from pydantic import BaseModel  # , field_validator
from typing import Optional

# from common.utils import nested_list_to_np


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
