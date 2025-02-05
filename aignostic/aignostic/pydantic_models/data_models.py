from pydantic import BaseModel, HttpUrl


class FetchDatasetRequest(BaseModel):
    """
    A model for a request to fetch a dataset
    """
    dataset_url: HttpUrl
    dataset_api_key: str


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


class ModelResponse(BaseModel):
    """
    A model for a response from a model

    Attributes:
        predictions: list[list] - the predictions from the model
    """
    predictions: list[list]
