from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from common.models import ModelInput, ModelResponse
import numpy as np

app: FastAPI = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EPSILON = 0.25
TEST_INPUT = [
    [1, 1, 1],
    [1, 2, 1],
    [1, 1, 1],
    [2, 3, 2],
    [2, 2, 2],
    [2, 1, 2],
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, -1]
]
TEST_INPUT_FORWARD = (np.array(TEST_INPUT) + EPSILON).tolist()
TEST_INPUT_BACKWARD = (np.array(TEST_INPUT) - EPSILON).tolist()
TEST_LABELS = [[1], [1], [1], [2], [2], [2], [3], [3], [3]]
TEST_LABELS_FORWARD = [[2], [2], [1], [2], [2], [2], [3], [1], [3]]
TEST_LABELS_BACKWARD = [[1], [1], [1], [1], [2], [3], [3], [3], [3]]
EXPECTED_GRADIENT = [
    [2, 2, 2],
    [2, 2, 2],
    [0, 0, 0],
    [2, 2, 2],
    [0, 0, 0],
    [-2, -2, -2],
    [0, 0, 0],
    [-4, -4, -4],
    [0, 0, 0]
]


@app.post('/predict', response_model=ModelResponse)
async def predict(input_data: ModelInput):
    if input_data.features == TEST_INPUT:
        return ModelResponse(predictions=TEST_LABELS)
    elif input_data.features == TEST_INPUT_FORWARD:
        return ModelResponse(predictions=TEST_LABELS_FORWARD)
    elif input_data.features == TEST_INPUT_BACKWARD:
        return ModelResponse(predictions=TEST_LABELS_BACKWARD)
    else:
        raise ValueError(f"Unexpected input data for test: {input_data.features}")
