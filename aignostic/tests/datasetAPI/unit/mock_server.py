from folktables import ACSDataSource
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np


app = FastAPI()


data_source = ACSDataSource(survey_year="2019", horizon="1-Year", survey="person")
acs_data = data_source.get_data(states=["AL"], download=True)


@app.get('/fetch-datapoints')
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
        acs_rows = acs_data.iloc[indices]
        acs_rows = acs_rows.replace({
            pd.NA: None,
            np.nan: None,
            float('inf'): None,
            float('-inf'): None
        })
        return JSONResponse(content={
            "column_names": acs_rows.columns.tolist(),
            "rows": acs_rows.values.tolist()
        })
    except Exception as e:
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
