from fastapi import FastAPI
from common.models import DatasetResponse, ModelResponse
from mocks.model.hf_utils import load_causal_LM, predict_causal_LM
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
model, tokenizer = load_causal_LM(model_name, tokenizer_name=tokenizer_name)


@app.get("/")
def read_root():
    return {"message": "Welcome to the TinyStories-1M Model API"}


@app.post("/predict", response_model=ModelResponse)
def predict(input: DatasetResponse) -> ModelResponse:

    output = predict_causal_LM(
        model=model,
        tokenizer=tokenizer,
        input=input,
        num_beams=1,
    )
    print(f"Model returing output: {output}")
    return output


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5027)
