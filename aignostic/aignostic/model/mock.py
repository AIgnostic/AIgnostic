from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

app = FastAPI()


class DataSet(BaseModel):
    data: pd.DataFrame

class QueryOutput(BaseModel):
    data: pd.DataFrame

@app.post("/query_all")
def predict(dataset : DataSet) -> QueryOutput:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return empty dataframe for now - fill this in with actual test models when trained 
    return QueryOutput(data=pd.DataFrame())

"""
TODO: (Low Priority) Extend to batch querying / single datapoint querying for convenience
(e.g. if dataset is very large)
"""