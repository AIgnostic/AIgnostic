from fastapi import FastAPI
from common.models import DatasetResponse, ModelResponse


app: FastAPI = FastAPI()


@app.post("/predict", response_model=ModelResponse)
def predict(input: DatasetResponse) -> ModelResponse:
    """
    Given a dataset, predict the expected outputs for the model
    NOTE: this is a mock implementation and is left blank on purpose
    """
    return ModelResponse(predictions=input.labels)
