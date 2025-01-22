from fastapi import FastAPI
from aignostic.pydantic_models.models import Data
import uvicorn


app = FastAPI(debug=True)


@app.post("/predict", response_model=Data)
def predict(dataset: Data) -> Data:
    """
    Given a dataset, predict the expected outputs for the model
    """
    print("Received POST req")
    # Return empty dataframe for now - fill this in with actual test models when trained
    return Data(column_names=[], rows=[[]])


"""
TODO: (Low Priority) Extend to batch querying
or single datapoint querying for convenience
(e.g. if dataset is very large)
"""


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)
