from folktables import ACSDataSource
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd


app = FastAPI()


data_source = ACSDataSource(survey_year="2018", horizon="1-Year", survey="person")
acs_data = data_source.get_data(states=["AL"], download=True)


@app.get('/acs-dataframe')
async def get_dataframe():
    """
    Retrieves a single row of data from the ACS dataset, converts it to a dictionary,
    and returns it in a JSON response as part of a dataset.
    """
    try:
        acs_row = acs_data.iloc[0]
        acs_dict = acs_row.replace({
            pd.NA: None,
            float('inf'): None,
            float('-inf'): None
        }).to_dict()
        return JSONResponse(content=[acs_dict])
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get('/invalid-data')
async def get_invalid_data():
    """
    Returns an invalid JSON response, which cannot be parsed into a DataFrame.
    """
    invalid_data = "This is not a valid JSON or tabular data"
    return JSONResponse(
        content={
            "error": "Invalid data format. Cannot be parsed into DataFrame.",
            "data": invalid_data
        },
        status_code=400
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
