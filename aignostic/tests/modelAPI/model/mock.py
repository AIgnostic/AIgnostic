from fastapi import FastAPI
from aignostic.pydantic_models.models import Data


app = FastAPI()


@app.post("/predict")
def predict(dataset: Data) -> Data:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return empty dataframe for now - fill this in with actual test models when trained
    return Data(column_names=[], rows=[[]])


"""
TODO: (Low Priority) Extend to batch querying
or single datapoint querying for convenience
(e.g. if dataset is very large)
"""
