from fastapi import FastAPI 
from pydantic import BaseModel
import numpy as np
from sklearn.pipeline import Pipeline
import pickle
from aignostic.pydantic_models.models import Data

app = FastAPI()

model : Pipeline = pickle.load(open('scikit_model.sav', 'rb'))

@app.post("/predict")
def predict(dataset : Data) -> Data:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return identical dataframe for now - fill this in with actual test models when trained
    out : np.array = model.predict(dataset.rows)
    rows = out.tolist() if len(dataset.rows) > 1 else [out.tolist()]
    return Data(column_names=None, rows=rows)

"""
TODO: (Low Priority) Extend to batch querying / single datapoint querying for convenience
(e.g. if dataset is very large)
"""