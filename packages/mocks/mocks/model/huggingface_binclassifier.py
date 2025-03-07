from fastapi import FastAPI
from common.models import DatasetResponse, ModelResponse
from mocks.model.hf_utils import predict_t2class as text_classification_predict

app = FastAPI()

# utilising hugging face high-level pipeline for sentiment analysis
# pipe = pipeline("text-classification", model="siebert/sentiment-roberta-large-english")
name = "siebert/sentiment-roberta-large-english"


@app.post("/predict", response_model=ModelResponse)
def predict(input: DatasetResponse) -> ModelResponse:
    return text_classification_predict(input, name)
