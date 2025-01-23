from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
import numpy as np
from sklearn.pipeline import Pipeline
import pickle
from aignostic.pydantic_models.data_models import DataSet
import os
app = FastAPI()


model: Pipeline = pickle.load(open(os.path.join(os.path.dirname(__file__), '../../../scikit_model.sav'), 'rb'))
MOCK_API_KEY = "scikit-mock-test-key"
api_key_header = APIKeyHeader(name="api-key", auto_error=False)

def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key_header == MOCK_API_KEY:
        return api_key_header
    raise HTTPException(status_code=401, detail="Unauthorised Access: Invalid API Key")


@app.post("/predict", dependencies=[Depends(get_api_key)])
def predict(dataset: DataSet) -> DataSet:
    """
    Given a dataset, predict the expected outputs for the model
    """
    headers = app.request.headers
    # Return identical dataframe for now - fill this in with actual test models when trained
    out: np.array = model.predict(dataset.rows)
    rows = out.tolist() if len(dataset.rows) > 1 else [out.tolist()]
    return DataSet(column_names=dataset.column_names, rows=rows)


"""
TODO: (Low Priority) Extend to batch querying / single datapoint querying for convenience
(e.g. if dataset is very large)
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=5001)
