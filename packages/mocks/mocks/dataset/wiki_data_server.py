"""
Mock dataserver for the WikiText-103 dataset for next-token generation.
"""

from fastapi import FastAPI, Query, Depends, HTTPException
import pandas as pd
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from datasets import load_dataset
from common.models import DatasetResponse
from mocks.api_utils import get_dataset_api_key

app: FastAPI = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load WikiText-103 dataset
dataset = load_dataset("wikitext", "wikitext-103-raw-v1")

# Convert dataset to DataFrame
old_df = pd.DataFrame(dataset["train"])

# Ensure dataset is formatted correctly
if "text" not in old_df.columns:
    raise ValueError("Dataset must contain a 'text' column.")


@app.get("/")
async def read_root():
    return {"message": "Welcome to the WikiText-103 Next Token server!"}


@app.get('/fetch-datapoints', dependencies=[Depends(get_dataset_api_key)], response_model=DatasetResponse)
async def fetch_datapoints(num_datapoints: int = Query(2, alias="n")):
    """
    Fetch num_datapoints raw text samples from WikiText-103 and return them as JSON in DatasetResponse format.
    The DatasetResponse will contain ONLY the 'features' field, which is a list of prompts.

    Args:
        num_datapoints (int): Number of text samples to fetch.

    Returns:
        JSONResponse: A JSON response containing the datapoints in DatasetResponse format.
                       Only the 'features' field will be populated.
    """
    df = old_df.dropna(subset=["text"])
    df = df[df["text"].str.strip().astype(bool)]
    dataset_size = len(df)
    print("dataset_size: ", dataset_size)
    if num_datapoints > dataset_size:
        raise HTTPException(
            status_code=400,
            detail="Requested more data points than available in the dataset."
        )
    print("num_datapoints: ", num_datapoints)
    random_indices = np.random.choice(dataset_size, num_datapoints, replace=False)
    print("random_indices: ", random_indices)
    try:
        selected_data = df.iloc[random_indices]["text"].tolist()

        features = [[prompt] for prompt in selected_data]
        print("features: ", features)
        print("length of features: ", len(features))
        return DatasetResponse(features=features, labels=[], group_ids=[])

    except Exception as e:
        raise HTTPException(detail=f"Error: {e}", status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5025)
