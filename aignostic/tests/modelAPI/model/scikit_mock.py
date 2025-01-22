from fastapi import FastAPI, HTTPException
import numpy as np
from sklearn.pipeline import Pipeline
import pickle
from aignostic.pydantic_models.models import Data
import uvicorn

app = FastAPI()

model: Pipeline = pickle.load(open('scikit_model.sav', 'rb'))


@app.post("/predict", response_model=Data)
def predict(dataset: Data) -> Data:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return identical dataframe for now - fill this in with actual test models when trained
    out: np.array = None
    try:
        out = model.predict(dataset.rows)
    except Exception:
        raise HTTPException(status_code=400, detail=str("Model cannot predict on given data"))
    rows = out.tolist() if len(dataset.rows) > 1 else [out.tolist()]
    return Data(column_names=[], rows=rows)


"""
TODO: (Low Priority) Extend to batch querying / single datapoint querying for convenience
(e.g. if dataset is very large)
"""
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)
