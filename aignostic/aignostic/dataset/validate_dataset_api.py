from pydantic import ValidationError
from aignostic.pydantic_models.data_models import ModelInput
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import requests
from urllib.parse import urlparse
import uvicorn

app = FastAPI()


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def fetch_data(url: str) -> dict:
    response = requests.get(url)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError as e:
        raise ValueError(f"Invalid JSON response: {str(e)}")


def parse_dataset(data: dict) -> ModelInput:
    try:
        dataset = ModelInput(column_names=data.get("column_names", []), rows=data.get("rows", []))
    except Exception as e:
        raise ValueError(f"Unable to parse data into DataFrame: {str(e)}")

    if any(len(dataset.column_names) != len(row) for row in dataset.rows):
        raise ValidationError("Number of column names not equal to the number of elements in one or more rows")

    return dataset


@app.get('/validate-dataset')
async def validate_dataset(url: str = Query(..., description="Dataset URL")):
    """
    Validate a dataset URL and return the columns and number of rows.
    """
    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL")

    try:
        data = fetch_data(url)
        dataset = parse_dataset(data)
        return JSONResponse(content={
            "message": "Data successfully parsed into DataFrame",
            "columns": dataset.column_names,
            "rows": len(dataset.rows)
        })

    # TODO: Add logging to exception handling
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Resource not found")
        else:
            raise HTTPException(status_code=400, detail="Failed to fetch data")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid data format")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)
