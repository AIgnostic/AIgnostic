from fastapi import FastAPI 
from pydantic import BaseModel
import numpy as np
from sklearn.pipeline import Pipeline
import pickle
from aignostic.pydantic_models.models import DataSet, QueryOutput, to_dataframe

app = FastAPI()

model : Pipeline = pickle.load(open('scikit_model.sav', 'rb'))

@app.post("/predict")
def predict(dataset : DataSet) -> QueryOutput:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return empty dataframe for now - fill this in with actual test models when trained
    if not dataset.columns:
        return QueryOutput(columns={})
    return QueryOutput(columns=model.predict(to_dataframe(dataset))).to_dict()

"""
TODO: (Low Priority) Extend to batch querying / single datapoint querying for convenience
(e.g. if dataset is very large)
"""