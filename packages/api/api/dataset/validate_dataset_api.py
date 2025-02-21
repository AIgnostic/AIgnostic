from pydantic import ValidationError
from api.pydantic_models.data_models import FetchDatasetRequest
from common.models import ModelInput

from fastapi import FastAPI, HTTPException
import requests
import uvicorn

app = FastAPI()


def _validate_dataset_format(data_to_validate: dict) -> ModelInput:
    try:
        data = ModelInput(**data_to_validate)
    except ValidationError as e:
        raise ValueError(f"Data format is invalid: {e}")

    features, labels, group_ids = data.features, data.labels, data.group_ids

    # Validate all lists have the same length
    if not (len(features) == len(labels) == len(group_ids)):
        raise ValueError("Features, labels, and group_ids must have the same number of rows.")

    # Validate inner list consistency in a single loop
    feature_length = len(features[0]) if features else 0
    label_length = len(labels[0]) if labels else 0

    for f_row, l_row in zip(features, labels):
        if len(f_row) != feature_length:
            raise ValueError("All feature rows must have the same number of elements.")
        if len(l_row) != label_length:
            raise ValueError("All label rows must have the same number of elements.")

    return data


@app.post("/fetch-data")
def fetch_dataset(request: FetchDatasetRequest) -> ModelInput:
    """
    Validate a dataset URL and parse the data to be used in the model.

    Params:
    - request : FetchDatasetRequest - Pydantic model for the request
    """
    headers = {"Authorization": f"Bearer {request.dataset_api_key}"} if request.dataset_api_key else {}

    try:
        response = requests.get(request.dataset_url, headers=headers)

        response.raise_for_status()

        data = response.json()
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.json()["detail"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while processing data: {e}")

    try:
        return _validate_dataset_format(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error while validating data: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)
