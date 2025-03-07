"""
Mock dataserver for the Financial PhraseBank dataset.
"""
from sklearn.datasets import fetch_openml
from fastapi import FastAPI, Query, Depends, HTTPException
import pandas as pd
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

boston = fetch_openml(name="boston", version=1, as_frame=True)
df: pd.DataFrame = boston.frame

# Select numeric features and label
BOSTON_FEATURES = ['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD', 'TAX', 'PTRATIO', 'B', 'LSTAT']
BOSTON_LABELS = 'MEDV'


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Boston Housing data server!"}


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

        features = selected_data[BOSTON_FEATURES].apply(pd.to_numeric, errors='coerce')
        labels = pd.to_numeric(selected_data[BOSTON_LABELS], errors='coerce')

        features = features.to_numpy().reshape(-1, len(BOSTON_FEATURES))
        labels = labels.to_numpy().reshape(-1, 1)
#
        return DatasetResponse(
            features=features.tolist(),
            labels=labels.tolist(),
            group_ids=[0] * len(features)  # No groups in this dataset
        )
    except Exception as e:
        return HTTPException(detail=f"Error: {e}", status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5013)
