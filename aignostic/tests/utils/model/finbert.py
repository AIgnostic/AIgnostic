from transformers import pipeline
from fastapi import FastAPI
from aignostic.pydantic_models.data_models import ModelInput, ModelResponse
from tests.utils.model.hf_utils import predict as text_classification_predict

app = FastAPI()
pipe = pipeline("text-classification", model="ProsusAI/finbert")


@app.post("/predict", response_model=ModelResponse)
def predict(input: ModelInput) -> ModelResponse:
    return text_classification_predict(input, pipe)
