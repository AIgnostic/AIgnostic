"""
Mock FinBERT model
"""
from fastapi import FastAPI
from common.models import DatasetResponse, ModelResponse
from mocks.model.hf_utils import load_t2class_model, predict_t2class
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
name = "ProsusAI/finbert"
model, tokenizer = load_t2class_model(name)


@app.get("/")
def read_root():
    return {"message": "Welcome to the FinBERT Model API"}


@app.post("/predict", response_model=ModelResponse)
def predict(input: DatasetResponse) -> ModelResponse:
    return predict_t2class(model, tokenizer, input)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
