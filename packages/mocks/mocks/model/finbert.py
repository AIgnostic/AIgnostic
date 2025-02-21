from fastapi import FastAPI
from common.models import ModelInput, ModelResponse
from mocks.model.hf_utils import predict as text_classification_predict

app = FastAPI()
# pipe = pipeline("text-classification", model="ProsusAI/finbert")
name = "ProsusAI/finbert"


@app.post("/predict", response_model=ModelResponse)
def predict(input: ModelInput) -> ModelResponse:
    return text_classification_predict(input, name)
