"""
Mock dataserver for the WikiText-103 dataset for next-token generation.
"""

from fastapi import FastAPI, Query, Depends, HTTPException
import pandas as pd
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from datasets import load_dataset
from mocks.api_utils import get_dataset_api_key
from common.models import LLMInput  # Ensure LLMInput is imported
import os

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
df = pd.DataFrame(dataset["train"])

# Ensure dataset is formatted correctly
if "text" not in df.columns:
    raise ValueError("Dataset must contain a 'text' column.")

# Function to generate context-next token pairs
def generate_next_token_pairs(df, num_samples=5000, context_length=20):
    data = []

    for text in df["text"]:
        words = text.split()
        if len(words) <= context_length:
            continue  # Skip short lines

        for i in range(len(words) - context_length):
            context = " ".join(words[i : i + context_length])
            next_token = words[i + context_length]
            data.append([context, next_token])

    return pd.DataFrame(data, columns=["context", "next_token"])

# Create processed dataset
processed_df = generate_next_token_pairs(df)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the WikiText-103 Next Token server!"}

@app.get('/fetch-datapoints', dependencies=[Depends(get_dataset_api_key)], response_model=LLMInput)
async def fetch_datapoints(num_datapoints: int = Query(2, alias="n"), max_length: int = Query(30)):
    """
    Fetch num_datapoints from WikiText-103 and return them as JSON in LLMInput format.

    Args:
        num_datapoints (int): Number of text samples to fetch.
        max_length (int): Maximum length of the generated sequence.

    Returns:
        JSONResponse: A JSON response containing the datapoints in LLMInput format.
    """
    dataset_size = len(processed_df)

    if num_datapoints > dataset_size:
        raise HTTPException(
            status_code=400,
            detail="Requested more data points than available in the dataset."
        )

    random_indices = np.random.choice(dataset_size, num_datapoints, replace=False)

    try:
        selected_data = processed_df.iloc[random_indices]

        prompts = selected_data["context"].tolist()

        return LLMInput(
            features=[prompt.split() for prompt in prompts],  # Convert text into tokenized format
            labels=[[selected_data["next_token"].tolist()[i]] for i in range(num_datapoints)],
            group_ids=[0] * num_datapoints,  # No groups in this dataset
            prompt=prompts[0],  # Use the first prompt as an example for LLMInput format
            max_length=max_length
        )
    except Exception as e:
        return HTTPException(detail=f"Error: {e}", status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5025)
