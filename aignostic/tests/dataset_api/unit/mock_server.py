
from folktables import ACSDataSource, ACSEmployment
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import logging
from aignostic.pydantic_models.data_models import ModelInput

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app: FastAPI = FastAPI()


data_source = ACSDataSource(survey_year="2018", horizon="1-Year", survey="person")
acs_data = data_source.get_data(states=["AL"], download=True)
features, label, group = ACSEmployment.df_to_pandas(acs_data)


@app.get('/fetch-datapoints', response_model=ModelInput)
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
        filtered_features = features.iloc[indices].replace({pd.NA: None, np.nan: None}).astype(str)
        filtered_labels = label.iloc[indices].replace({pd.NA: None, np.nan: None}).astype(str)
        filtered_group_ids = group.iloc[indices].replace({pd.NA: None, np.nan: None})

        print(filtered_features)
        filtered_features = list(list(r) for r in filtered_features.values)
        filtered_labels = list(list(r) for r in filtered_labels.values)
        filtered_group_ids = list(filtered_group_ids.values)

        dataset = ModelInput(
            features=filtered_features,
            labels=filtered_labels,
            group_ids=filtered_group_ids
        )

        return JSONResponse(content=dataset.dict(), status_code=200)
       

    except Exception as e:
        logger.error("Error fetching datapoints: %s", str(e))
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
