"""
Mock FinBERT model
"""
from transformers import pipeline
from fastapi import FastAPI
from common.models import ModelInput, ModelResponse
from mocks.model.hf_utils import predict as text_classification_predict
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

pipe = pipeline("text-classification", model="ProsusAI/finbert")


@app.post("/predict", response_model=ModelResponse)
def predict(input: ModelInput) -> ModelResponse:
    return text_classification_predict(input, pipe)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
