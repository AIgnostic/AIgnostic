
from folktables import ACSDataSource, ACSEmployment
from fastapi import FastAPI, Body, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
import pandas as pd

import numpy as np
from aignostic.pydantic_models.data_models import df_to_JSON
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

MOCK_API_KEY = "dataset-api-key"
api_key_header = APIKeyHeader(name="api-key", auto_error=False)
data_source = ACSDataSource(survey_year="2018", horizon="1-Year", survey="person")
acs_data = data_source.get_data(states=["AL"], download=True)
features, label, group = ACSEmployment.df_to_pandas(acs_data)

def get_api_key(api_key: str = Depends(api_key_header)):
    if (api_key_header == MOCK_API_KEY):
        return api_key_header
    raise HTTPException(status_code=401, detail="Unauthorised Access: Invalid API Key")

@app.get('/fetch-datapoints')

async def fetch_datapoints(indices: list[int] = Body([0, 1]), dependencies=[Depends(get_api_key)]):
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

        acs_datapoints = pd.concat([features.iloc[indices], label.iloc[indices]], axis=1)
        acs_datapoints = acs_datapoints.replace({
            pd.NA: None,
            np.nan: None,
            float('inf'): None,
            float('-inf'): None
        })

        return JSONResponse(content=df_to_JSON(acs_datapoints), status_code=200)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get('/invalid-data')
async def get_invalid_data():
    """
    Returns an invalid JSON response, which cannot be parsed into our expected
    Pydantic model.
    """
    return JSONResponse(
        content={
            "column_names": "This is not a list as expected",
            "rows": []
        },
        status_code=200
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
