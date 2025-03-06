"""
Mock dataserver for the Financial PhraseBank dataset.
"""

from fastapi import FastAPI, Query, Depends, HTTPException
import pandas as pd
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from mocks.api_utils import get_dataset_api_key
from common.models import DatasetResponse
import os

app: FastAPI = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Financial PhraseBank data
DATA_PATH = os.path.join(os.path.dirname(__file__),
                         "FinancialPhraseBank-v1.0",
                         "Sentences_50Agree.txt")
df = pd.read_csv(DATA_PATH, delimiter=".@", names=["text", "sentiment"], encoding="ISO-8859-1")


# Ensure the dataset has expected columns (Modify as needed)
if not {'text', 'sentiment'}.issubset(df.columns):
    raise ValueError("Dataset must contain 'text' and 'sentiment' columns.")


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
    dataset_size = len(df)

    if num_datapoints > dataset_size:
        raise HTTPException(
            status_code=400,
            detail="Requested more data points than available in the dataset.")

    random_indices = np.random.choice(dataset_size, num_datapoints, replace=False)

    try:
        selected_data = df.iloc[random_indices]

        features = [[text] for text in selected_data["text"].tolist()]
        labels = [[sentiment] for sentiment in selected_data["sentiment"].tolist()]

        return DatasetResponse(
            features=features,
            labels=labels,
            group_ids=[0] * len(features)  # No groups in this dataset
        )
    except Exception as e:
        return HTTPException(detail=f"Error: {e}", status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5024)
