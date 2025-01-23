from fastapi import FastAPI
import numpy as np
from sklearn.pipeline import Pipeline
import pickle
from aignostic.pydantic_models.data_models import DataSet
import os
app = FastAPI()


model: Pipeline = pickle.load(open(os.path.join(os.path.dirname(__file__), '../../../scikit_model.sav'), 'rb'))


@app.post("/predict")
def predict(dataset: DataSet) -> DataSet:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return identical dataframe for now - fill this in with actual test models when trained
    out: np.ndarray = model.predict(dataset.rows)
    rows: list[list] = out.tolist() if len(dataset.rows) > 1 else [out.tolist()]
    return DataSet(column_names=dataset.column_names, rows=rows)


"""
TODO: (Low Priority) Extend to batch querying / single datapoint querying for convenience
(e.g. if dataset is very large)
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=5001)
