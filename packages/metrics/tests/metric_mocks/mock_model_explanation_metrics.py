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


@app.post('/predict-non-numeric-ESS', response_model=ModelResponse)
async def predict_non_numeric(input_data: DatasetResponse):
    return ModelResponse(
        predictions=[['Positive'] for _ in range(len(input_data.features))],
        confidence_scores=[[1] for _ in range(len(input_data.features))]
    )


@app.post('/predict-10000-ESS', response_model=ModelResponse)
async def predict_10000(input_data: DatasetResponse):
    return ModelResponse(
        predictions=[[10000] for _ in range(len(input_data.features))],
        confidence_scores=[[1] for _ in range(len(input_data.features))]
    )


@app.post('/predict-different-ESS', response_model=ModelResponse)
async def predict_different(input_data: DatasetResponse):
    return ModelResponse(
        predictions=[[random.random()] for _ in range(len(input_data.features))],
        confidence_scores=[[random.random()] for _ in range(len(input_data.features))]
    )

# Any arbitrary sequence should work as the predictions are always the same
PERFECT_ESP_INPUT_FEATURES = (
    [[1, 123, 1, 3, 13, 1, 1, -50001, 13444, 1]] * 10
    + [[0, 1, 0, 4, 2, 1, 10000, 30, 2, 9493]] * 10
    + [[1, 0, 0, 20000, 3, 1, 80, 40, 1, 9432]] * 10
)


@app.post('/predict-perfect-ESP', response_model=ModelResponse)
async def predict_esp(input_data: DatasetResponse):
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
async def predict_bivariate_esp(input_data: DatasetResponse):
    # predictions required to test regression, confidence_scores required to test classification
    predictions = [[100]] * 10 + [[0]] * 10 + [[-180]] * 10
    confidence_scores = [[1]] * 10 + [[0]] * 10 + [[0.3]] * 10
    return ModelResponse(
        predictions=predictions,
        confidence_scores=confidence_scores
    )

FIDELITY_MARGIN = 0.05


@app.post('/predict-perfect-fidelity', response_model=ModelResponse)
async def predict_fidelity(input_data: DatasetResponse):
    return ModelResponse(
        # Predictions used for regression
        predictions=input_data.labels,
        # Confidence scores used for classification
        confidence_scores=[[1]] * len(input_data.features)
    )

BAD_FIDELITY_INPUT_FEATURES = (
    [[1], [1], [1], [1]]
)
BAD_FIDELITY_EXPECTED_SCORE = 0


@app.post('/predict-bad-fidelity', response_model=ModelResponse)
async def predict_bad_fidelity(input_data: DatasetResponse):
    confidence_scores = []
    # Maximise distance between confidence_scores
    for p in input_data.features:
        if p[0] < 0.5:
            confidence_scores.append([1])
        else:
            confidence_scores.append([0])
    return ModelResponse(
        # Predictions used for regression
        predictions=[[0] for _ in range(len(input_data.features))],
        # Confidence scores used for classification
        confidence_scores=confidence_scores
    )
