from fastapi import FastAPI
import numpy as np
from sklearn.pipeline import Pipeline
import pickle
from aignostic.pydantic_models.data_models import ModelInput, ModelResponse
import os#
import logging
from fastapi import HTTPException

app = FastAPI()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

model: Pipeline = pickle.load(open(os.path.join(os.path.dirname(__file__), '../../../scikit_model.sav'), 'rb'))

@app.post("/predict", response_model = ModelResponse)
def predict(input: ModelInput) -> ModelResponse:
    """
    Given a dataset, predict the expected outputs for the model
    """
    try:
        if input.features == [[]]:
            return ModelResponse(predictions=input.features)
        output: np.ndarray = model.predict(input.features)
        predictions : list[list] = output.tolist() if len(input.features) > 1 else [output.tolist()]
    except Exception as e:
        return HTTPException(detail=f"Error occured during model prediction: {e}", status_code=500)
    return ModelResponse(predictions=predictions)


"""
TODO: (Low Priority) Extend to batch querying / single datapoint querying for convenience
(e.g. if dataset is very large)
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=5001)
