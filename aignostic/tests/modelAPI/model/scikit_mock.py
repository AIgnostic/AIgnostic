from fastapi import FastAPI
import numpy as np
from sklearn.pipeline import Pipeline
import pickle
from aignostic.pydantic_models.models import Data
import uvicorn
import pandas as pd
from folktables import ACSDataSource, ACSEmployment

app = FastAPI()

model: Pipeline = pickle.load(open('/home/tisya/AIgnostic/aignostic/scikit_model.sav', 'rb'))


@app.get('/predict')
def predict() -> Data:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Import the folktables dataset and load the employment data
    data_source: ACSDataSource = ACSDataSource(survey_year='2018', horizon='1-Year', survey='person')
    acs_data: pd.DataFrame = data_source.get_data(states=[
        "AL"
    ], download=True)[0:1]
    features, _, _ = ACSEmployment.df_to_numpy(acs_data)

    return Data(column_names=None, rows=features.tolist())
    # Return identical dataframe for now - fill this in with actual test models when trained

    # if the method is GET, then return hello world

    # if the method is POST, then the dataset is in the body of the request

    

@app.post("/predict", response_model=Data)
def predict(dataset: Data) -> Data:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return identical dataframe for now - fill this in with actual test models when trained
    out: np.array = None
    try:
        out = model.predict(dataset.rows)
    except Exception as e:
        print("Error while predicting:", e)
        return Data(column_names=None, rows=[[]])
    
    rows = out.tolist() if len(dataset.rows) > 1 else [out.tolist()]
    return Data(column_names=None, rows=rows)


"""
TODO: (Low Priority) Extend to batch querying / single datapoint querying for convenience
(e.g. if dataset is very large)
"""

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)