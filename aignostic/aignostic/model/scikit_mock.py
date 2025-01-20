from fastapi import FastAPI
from sklearn.pipeline import Pipeline
import pickle
from aignostic.pydantic_models.models import DataSet, QueryOutput

app = FastAPI()

model: Pipeline = pickle.load(open("scikit_model.sav", "rb"))


@app.post("/query_all")
def predict(dataset: DataSet) -> QueryOutput:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return empty dataframe for now - fill this in with actual test models when trained
    return QueryOutput(model.predict(dataset.to_dataframe()))


"""
TODO: (Low Priority) Extend to batch querying / single datapoint querying for convenience
(e.g. if dataset is very large)
"""
