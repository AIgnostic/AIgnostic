from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from common.models import ModelInput, ModelResponse

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
    [1, 2],
    [2, 2],
]
INPUTS_TO_LABELS = {
    (1, 2): [1],
    (2, 2): [2],
    (1.25, 2): [2],
    (2.25, 2): [2],
    (1, 2.25): [1.5],
    (2, 2.25): [2],
    (0.75, 2): [1],
    (1.75, 2): [2],
    (1, 1.75): [1.75],
    (2, 1.75): [1]
}
EXPECTED_GRADIENT = [
    [2, -0.5],
    [0, 2]
]


@app.post('/predict', response_model=ModelResponse)
async def predict(input_data: ModelInput):
    try:
        predictions = [INPUTS_TO_LABELS[tuple(row)] for row in input_data.features]
        return ModelResponse(
            predictions=predictions
        )
    except KeyError:
        raise KeyError(f"Input data {input_data} not in test data - Update tests / mock to include this")
