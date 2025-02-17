from pydantic import BaseModel, HttpUrl


class FetchDatasetRequest(BaseModel):
    """
    A model for a request to fetch a dataset
    """
    dataset_url: HttpUrl
    dataset_api_key: str
