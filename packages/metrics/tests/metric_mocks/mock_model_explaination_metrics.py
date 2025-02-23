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

BIVARIATE_ESP_INPUT_FEATURES = (
    [[0, 1, 0, 4, 2, 1, 10000, 30, 2, 9493]] * 10
    + [[1, 0, 0, 2, 3, 1, 80, 40, 1, 9432]] * 10
    + [[0, 1, 0, 4, 2, 1, 23331, 30, 2, 1]] * 10 
)
BIVARIATE_ESP_EXPECTED_SCORE = 0.8
BIVARIATE_ESP_MARGIN = 0.15


@app.post('/predict-bivariate-ESP', response_model=ModelResponse)
async def predict_bivariate_esp(input_data: ModelInput):
    # predictions required to test regression, confidence_scores required to test classification
    predictions = [[100]] * 10 + [[0]] * 10 + [[-180]] * 10
    confidence_scores = [[1]] * 10 + [[0]] * 10 + [[0.3]] * 10
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
