from fastapi import FastAPI, Depends
import numpy as np
from sklearn.pipeline import Pipeline
import pickle
from tests.utils.api_utils import get_model_api_key
from aignostic.pydantic_models.data_models import ModelInput, ModelResponse
import os
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model: Pipeline = pickle.load(open(os.path.join(os.path.dirname(__file__), '../../../scikit_model.sav'), 'rb'))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Scikit-Learn Model API"}


@app.post("/predict", dependencies=[Depends(get_model_api_key)], response_model=ModelResponse)
def predict(input: ModelInput) -> ModelResponse:
    """
    Given a dataset, predict the expected outputs for the model
    """
    try:
        print(input.features)
        print(input.labels)
        print(input.group_ids)
        if not input.features or input.features == [[]]:
            return ModelResponse(predictions=input.features)
        output: np.ndarray = model.predict(input.features).reshape(-1, 1)
        predictions: list[list] = output.tolist()
        print(predictions)
    except Exception as e:
        raise HTTPException(detail=f"Error occured during model prediction: {e}", status_code=500)
    return ModelResponse(predictions=predictions)


"""
TODO: (Low Priority) Extend to batch querying / single datapoint querying for convenience
(e.g. if dataset is very large)
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
