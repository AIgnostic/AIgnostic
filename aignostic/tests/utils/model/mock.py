from fastapi import FastAPI
from aignostic.pydantic_models.data_models import DataSet


app: FastAPI = FastAPI()


@app.post("/predict")
def predict(dataset: DataSet) -> DataSet:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return empty dataframe for now - fill this in with actual test models when trained
    return DataSet(column_names=[], rows=[[]])


"""
TODO: (Low Priority) Extend to batch querying
or single datapoint querying for convenience
(e.g. if dataset is very large)
"""
