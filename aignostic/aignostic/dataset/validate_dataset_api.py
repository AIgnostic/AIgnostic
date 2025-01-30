from pydantic import ValidationError
from aignostic.pydantic_models.data_models import ModelInput, FetchDatasetRequest
from fastapi import FastAPI, HTTPException
import requests
import uvicorn

app = FastAPI()


@app.get("/fetch-data")
def fetch_dataset(request: FetchDatasetRequest) -> ModelInput:
    """
    Validate a dataset URL and parse the data to be used in the model.

    Params:
    - request : FetchDatasetRequest - Pydantic model for the request
    """
    try:
        headers = {"Authorization": f"Bearer {request.dataset_api_key}"} if request.dataset_api_key else {}
        response = requests.get(request.dataset_url, headers=headers)

        response.raise_for_status()

        data = response.json()
        return ModelInput(**data)
    except requests.exceptions.RequestException as e:
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized access: Please check your API Key")
        raise HTTPException(status_code=400, detail=f"Error while fetching data: {e}")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while fetching data: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)
