from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from common.models import DatasetResponse, ModelResponse
import random

app: FastAPI = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/predict', response_model=ModelResponse)
async def get_prediction_and_confidence(input_data: DatasetResponse):
    n = len(input_data.features)
    predictions = [[random.randint(0, 1)] for _ in range(n)]
    confidence_scores: list[list] = [[round(random.uniform(0.5, 1.0), 2)] for _ in range(n)]
    return ModelResponse(predictions=predictions, confidence_scores=confidence_scores)
