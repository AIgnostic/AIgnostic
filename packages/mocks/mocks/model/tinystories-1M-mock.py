from fastapi import FastAPI
from common.models import ModelInput, ModelResponse
from mocks.model.hf_utils import predict_causal_LM

app = FastAPI()

# utilising hugging face high-level pipeline for sentiment analysis
model_name = "roneneldan/TinyStories-1M"
tokenizer_name = "EleutherAI/gpt-neo-125M"

@app.post("/predict", response_model=ModelResponse)
def predict(input: ModelInput) -> ModelResponse:
    return predict_causal_LM(
        input,
        model_name,
        tokenizer_name=tokenizer_name,
        max_length=50,
        num_beams=1
    )
