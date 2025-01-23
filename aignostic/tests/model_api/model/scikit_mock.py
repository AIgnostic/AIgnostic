from fastapi import FastAPI
import numpy as np
from sklearn.pipeline import Pipeline  # type: ignore
import pickle
from aignostic.pydantic_models.data_models import DataSet

app = FastAPI()

model: Pipeline = pickle.load(open('scikit_model.sav', 'rb'))


@app.post("/predict")
def predict(dataset: DataSet) -> DataSet:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return identical dataframe for now - fill this in with actual test models when trained
    out: np.ndarray = model.predict(dataset.rows)
    rows: list[list] = list(out) if len(dataset.rows) > 1 else [list(out)]
    return DataSet(column_names=dataset.column_names, rows=rows)


"""
TODO: (Low Priority) Extend to batch querying / single datapoint querying for convenience
(e.g. if dataset is very large)
"""
