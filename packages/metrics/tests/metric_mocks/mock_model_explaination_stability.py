from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from common.models import ModelInput, ModelResponse
import random

app: FastAPI = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/predict-10000', response_model=ModelResponse)
async def predict_10000(input_data: ModelInput):
    return ModelResponse(
        predictions=[[10000] for _ in range(len(input_data.features))],
        confidence_scores=[[1] for _ in range(len(input_data.features))]
    )


@app.post('/predict-different', response_model=ModelResponse)
async def predict_different(input_data: ModelInput):
    return ModelResponse(
        predictions=[[random.random()] for _ in range(len(input_data.features))],
        confidence_scores=[[random.random()] for _ in range(len(input_data.features))]
    )
