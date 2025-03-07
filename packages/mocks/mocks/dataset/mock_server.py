from folktables import ACSDataSource, ACSEmployment
from fastapi import FastAPI, Query, Depends, HTTPException
from mocks.api_utils import get_dataset_api_key
from common.models import DatasetResponse
import pandas as pd
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

app: FastAPI = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


data_source = ACSDataSource(survey_year="2018", horizon="1-Year", survey="person")
acs_data = data_source.get_data(states=["AL"], download=True)
features, labels, groups = ACSEmployment.df_to_pandas(acs_data)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Folktables data server!"}


@app.get('/fetch-datapoints', dependencies=[Depends(get_dataset_api_key)], response_model=DatasetResponse)
async def fetch_datapoints(num_datapoints: int = Query(2, alias="n")):
    """
    Fetch num_datapoints from the ACS data and convert into
    our expected JSON format, returning it in a JSON response. Defaults to
    fetching the first row of the ACS data.

    Args:
        num_datapoints (int): Number of datapoints to fetch from the ACS data.
    Returns:
        JSONResponse: A JSON response containing the datapoints.
    """
    assert (len(features) == len(labels))
    assert (len(labels) == len(groups))
    dataset_size = len(features)

    random_indices = np.random.choice(dataset_size, num_datapoints, replace=False)

    def filter_fn(x, indices):
        return x.iloc[indices].replace({
            pd.NA: None,
            np.nan: None,
            float('inf'): None,
            float('-inf'): None
        })

    try:
        filtered_features = filter_fn(features, random_indices)
        filtered_labels = filter_fn(labels, random_indices)
        filtered_group_ids = filter_fn(groups, random_indices)

        filtered_features = [list(r) for r in filtered_features.values]
        filtered_labels = [[(bool(r) if isinstance(r, np.bool_) else r) for r in row] for row in filtered_labels.values]
        filtered_group_ids = list(filtered_group_ids.values)

        return DatasetResponse(
            features=filtered_features,
            labels=filtered_labels,
            group_ids=filtered_group_ids
        )
    except Exception as e:
        return HTTPException(detail=f"error: {e}", status_code=500)


@app.get('/invalid-data-format', dependencies=[Depends(get_dataset_api_key)])
async def invalid_data_format():
    return {"features": [[1, 2], [3, 4, 5]], "labels": [[1, 2], [3, 4]], "group_ids": [1, 2]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5010)
