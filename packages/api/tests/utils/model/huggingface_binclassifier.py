from transformers import pipeline
from fastapi import FastAPI
from api.pydantic_models.data_models import DatasetResponse, ModelResponse
from tests.utils.model.hf_utils import predict as text_classification_predict

app = FastAPI()

# utilising hugging face high-level pipeline for sentiment analysis
pipe = pipeline("text-classification", model="siebert/sentiment-roberta-large-english")


@app.post("/predict", response_model=ModelResponse)
def predict(input: DatasetResponse) -> ModelResponse:
    return text_classification_predict(input, pipe)
