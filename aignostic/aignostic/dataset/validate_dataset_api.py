from pydantic import ValidationError
from aignostic.pydantic_models.models import DataSet
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import requests
import pandas as pd
from urllib.parse import urlparse
import uvicorn

app = FastAPI()


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def fetch_data(url: str) -> list[dict]:
    response = requests.get(url)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError as e:
        raise ValueError(f"Invalid JSON response: {str(e)}")


def validate_dataframe(data: list[dict]) -> pd.DataFrame:
    dataset = DataSet(columns=data)
    try:
        return pd.DataFrame(dataset.columns)
    except Exception as e:
        raise ValueError(f"Unable to parse data into DataFrame: {str(e)}")


@app.get('/validate_dataset')
async def validate_dataset_url(url: str = Query(..., description="The URL of the dataset")):
    """
    Validate a dataset URL and return the columns and number of rows.
    """
    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL")

    try:
        data = fetch_data(url)
        dataframe = validate_dataframe(data)

        return JSONResponse(content={
            "message": "Data successfully parsed into DataFrame",
            "columns": dataframe.columns.tolist(),
            "rows": dataframe.shape[0]
        })
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Failed to fetch data")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {e.errors()}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)
