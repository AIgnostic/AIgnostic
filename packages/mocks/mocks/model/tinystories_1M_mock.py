from fastapi import FastAPI
from common.models import DatasetResponse, ModelResponse
from mocks.model.hf_utils import predict_causal_LM
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# utilising hugging face high-level pipeline for sentiment analysis
model_name = "roneneldan/TinyStories-1M"
tokenizer_name = "EleutherAI/gpt-neo-125M"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the TinyStories-1M Model API"}


@app.post("/predict", response_model=ModelResponse)
def predict(input: DatasetResponse) -> ModelResponse:

    return predict_causal_LM(
        input,
        model_name,
        tokenizer_name=tokenizer_name,
        max_length=50,
        num_beams=1,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)
