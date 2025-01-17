from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np

app = FastAPI()


class DataSet(BaseModel):
    data: np.ndarray


class QueryOutput(BaseModel):
    data: np.ndarray


@app.post("/query_all")
def predict(dataset: DataSet) -> QueryOutput:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return empty dataframe for now - fill this in with actual test models when trained
    return QueryOutput(data=np.array([]))


"""
TODO: (Low Priority) Extend to batch querying
or single datapoint querying for convenience
(e.g. if dataset is very large)
"""
