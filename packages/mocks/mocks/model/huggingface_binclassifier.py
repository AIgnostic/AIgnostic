from fastapi import FastAPI
from common.models import DatasetResponse, ModelResponse
from mocks.model.hf_utils import load_t2class_model, predict_t2class

app = FastAPI()

# utilising hugging face high-level pipeline for sentiment analysis
# pipe = pipeline("text-classification", model="siebert/sentiment-roberta-large-english")
name = "siebert/sentiment-roberta-large-english"

model, tokenizer = load_t2class_model(name)


@app.post("/predict", response_model=ModelResponse)
def predict(input: DatasetResponse) -> ModelResponse:
    return predict_t2class(model, tokenizer, input)
