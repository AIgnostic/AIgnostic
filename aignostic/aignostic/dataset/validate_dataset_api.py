from pydantic import ValidationError, HttpUrl
from aignostic.pydantic_models.data_models import ModelInput
from fastapi import FastAPI, HTTPException
import requests
import uvicorn

app = FastAPI()


@app.get("/fetch-data")
async def fetch_data(dataset_url: HttpUrl, api_key: str) -> ModelInput:
    """
    Validate a dataset URL and parse the data to be used in the model.

    Params:
    - dataset_url : HttpUrl - the URL of the dataset
    - api_key : str - the API key for the dataset
    """
    try:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        response = requests.get(dataset_url, headers=headers)

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
