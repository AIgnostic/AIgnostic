from pydantic import BaseModel


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
