
"""
Mock dataserver for the Financial PhraseBank dataset.
"""

from datasets import load_dataset
from fastapi import FastAPI, Query, Depends, HTTPException
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from mocks.api_utils import get_dataset_api_key
from common.models import DatasetResponse

app: FastAPI = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ds = load_dataset("roneneldan/TinyStories")


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Financial PhraseBank server!"}


@app.get('/fetch-datapoints', dependencies=[Depends(get_dataset_api_key)], response_model=DatasetResponse)
async def fetch_datapoints(num_datapoints: int = Query(2, alias="n")):
    """
    Fetch num_datapoints from the Financial PhraseBank and return them as JSON.

    Args:
        num_datapoints (int): Number of financial phrases to fetch.
    Returns:
        JSONResponse: A JSON response containing the datapoints.
    """
    print(f"ds.num_rows: {ds.num_rows}")

    dataset_size = ds.num_rows['validation']

    if num_datapoints > dataset_size:
        raise HTTPException(
            status_code=400,
            detail="Requested more data points than available in the dataset.")

    random_indices = np.random.choice(dataset_size, num_datapoints, replace=False)

    try:
        # print(f"validation data: {ds['validation']}")
        # print(f"texts: {ds['validation']['text']}")
        selected_data = ds['validation'].select(random_indices)
        texts = selected_data['text']
        # print(f"texts for sample: {texts}")
        features = [[text[:len(text) // 2]] for text in texts]
        labels = [[text[len(text) // 2:]] for text in texts]

        return DatasetResponse(
            features=features,
            labels=labels,
            group_ids=[0] * len(texts)  # No groups in this dataset
        )
    except Exception as e:
        return HTTPException(detail=f"Error: {e}", status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5026)
