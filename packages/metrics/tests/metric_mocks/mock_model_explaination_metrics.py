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


@app.post('/predict-10000-ESS', response_model=ModelResponse)
async def predict_10000(input_data: ModelInput):
    return ModelResponse(
        predictions=[[10000] for _ in range(len(input_data.features))],
        confidence_scores=[[1] for _ in range(len(input_data.features))]
    )


@app.post('/predict-different-ESS', response_model=ModelResponse)
async def predict_different(input_data: ModelInput):
    return ModelResponse(
        predictions=[[random.random()] for _ in range(len(input_data.features))],
        confidence_scores=[[random.random()] for _ in range(len(input_data.features))]
    )


@app.post('/predict-perfect-ESP', response_model=ModelResponse)
async def predict_esp(input_data: ModelInput):
    return ModelResponse(
        predictions=[[1] for _ in range(len(input_data.features))],
        confidence_scores=[[1] for _ in range(len(input_data.features))]
    )


@app.post('/predict-bivariate-ESP', response_model=ModelResponse)
async def predict_bivariate_esp(input_data: ModelInput):
    assert len(input_data.features) > 10, (
        "Input data must have more than 10 samples (arbitrarily decided) for a valid test"
    )
    midpoint = len(input_data.features) // 2

    # predictions required to test regression, confidence_scores required to test classification
    predictions = [[1] for _ in range(midpoint)] + [[0] for _ in range(midpoint, len(input_data.features))]
    confidence_scores = predictions
    return ModelResponse(
        predictions=predictions,
        confidence_scores=confidence_scores
    )


@app.post('/predict-perfect-fidelity', response_model=ModelResponse)
async def predict_fidelity(input_data: ModelInput):
    return ModelResponse(
        # Predictions used for regression
        predictions=input_data.predictions,
        # Confidence scores used for classification
        confidence_scores=input_data.confidence_scores
    )


@app.post('/predict-bad-fidelity', response_model=ModelResponse)
async def predict_bad_fidelity(input_data: ModelInput):
    confidence_scores = []
    # Maximise distance between confidence_scores
    for p in input_data.confidence_scores:
        if p < 0.5:
            confidence_scores.append([1])
        else:
            confidence_scores.append([0])
    return ModelResponse(
        # Predictions used for regression
        predictions=[[0] for _ in range(len(input_data.features))],
        # Confidence scores used for classification
        confidence_scores=confidence_scores
    )
