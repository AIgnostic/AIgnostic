from fastapi import FastAPI, Depends
import numpy as np
from sklearn.pipeline import Pipeline
from mocks.api_utils import get_model_api_key
from mocks.utils import load_scikit_model
from common.models import ModelInput, ModelResponse
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


model: Pipeline = load_scikit_model()


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
