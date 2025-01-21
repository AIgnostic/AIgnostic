from fastapi import FastAPI
import numpy as np
from sklearn.pipeline import Pipeline
import pickle
from aignostic.pydantic_models.models import Data
import uvicorn

app = FastAPI()

model: Pipeline = pickle.load(open('/home/tisya/AIgnostic/aignostic/scikit_model.sav', 'rb'))


@app.get('/predict')
def predict() -> Data:
    """
    Given a dataset, predict the expected outputs for the model
    """

    return Data(column_names=None, rows=[["Hello", "World"]])
    # Return identical dataframe for now - fill this in with actual test models when trained

    # if the method is GET, then return hello world

    # if the method is POST, then the dataset is in the body of the request
    

@app.post("/predict")
def predict(dataset: Data) -> Data:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return identical dataframe for now - fill this in with actual test models when trained
    out: np.array = model.predict(dataset.rows)
    rows = out.tolist() if len(dataset.rows) > 1 else [out.tolist()]
    return Data(column_names=None, rows=rows)


"""
TODO: (Low Priority) Extend to batch querying / single datapoint querying for convenience
(e.g. if dataset is very large)
"""


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)