from fastapi import FastAPI
import pandas as pd
from aignostic.pydantic_models.models import DataSet, QueryOutput


app = FastAPI()


@app.post("/predict")
def predict(dataset: DataSet) -> QueryOutput:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return empty dataframe for now - fill this in with actual test models when trained
    return QueryOutput(pd.DataFrame().to_dict())


"""
TODO: (Low Priority) Extend to batch querying
or single datapoint querying for convenience
(e.g. if dataset is very large)
"""
