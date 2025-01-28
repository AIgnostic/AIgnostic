
from folktables import ACSDataSource, ACSEmployment
from fastapi import FastAPI, Body, Depends, HTTPException
from tests.utils.api_utils import get_dataset_api_key
from aignostic.pydantic_models.data_models import ModelInput
import pandas as pd
import numpy as np

app: FastAPI = FastAPI()

data_source = ACSDataSource(survey_year="2018", horizon="1-Year", survey="person")

acs_data = data_source.get_data(states=["AL"], download=True)
features, label, group = ACSEmployment.df_to_pandas(acs_data)


@app.get('/fetch-datapoints', dependencies=[Depends(get_dataset_api_key)], response_model=ModelInput)
async def fetch_datapoints(indices: list[int] = Body([0, 1])):
    """
    Given a list of indices, fetch the data at each index and convert into
    our expected JSON format, and returns it in a JSON response. Defaults to
    fetching the first row of the ACS data.

    Args:
        indices (list[int]): A list of indices to fetch from the ACS data.
    Returns:
        JSONResponse: A JSON response containing the random datapoints.
    """
    try:
        filtered_features = features.iloc[indices].replace({
            pd.NA: None,
            np.nan: None,
            float('inf'): None,
            float('-inf'): None
            })
        filtered_labels = label.iloc[indices].replace({
            pd.NA: None,
            np.nan: None,
            float('inf'): None,
            float('-inf'): None
            })
        filtered_group_ids = group.iloc[indices].replace({
            pd.NA: None,
            np.nan: None,
            float('inf'): None,
            float('-inf'): None
            })

        filtered_features = list(list(r) for r in filtered_features.values)
        filtered_labels = [[(bool(r) if isinstance(r, np.bool_) else r for r in row)] for row in filtered_labels.values]
        filtered_group_ids = list(filtered_group_ids.values)

        return ModelInput(
            features=filtered_features,
            labels=filtered_labels,
            group_ids=filtered_group_ids
        )
    except Exception as e:
        return HTTPException(detail=f"error: {e}", status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
