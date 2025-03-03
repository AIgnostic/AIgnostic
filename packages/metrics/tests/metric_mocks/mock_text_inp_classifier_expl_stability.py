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

TEST_INPUT = ModelInput(
    features=[
        ["The company's shares rose 20 pc after the announcement of the new product line."],
        ["The company's bankruptcy filing caused a massive sell-off, leading to a sharp decline in stock prices."]
    ],
    labels=[
        ['positive'],
        ['negative']
    ],
    group_ids=[0] * 2
)


def generate_test_responses(stability: str, num_samples):
    """
    Generate test responses for high or low stability

    :param stability: str ['high' or 'low'] - the stability of the model responses
    :param multiplier: int - the number of times to repeat the test input
    :return: ModelResponse - the model response object
    """
    predictions = []
    if stability == "high":
        predictions = [
            ['positive']
        ] * num_samples
        confidence_scores = [[0.9]] * num_samples
    elif stability == "low":
        classes = ['positive', 'negative', 'neutral']
        predictions = np.random.choice(classes, size=(num_samples, 1), p=[0.34, 0.33, 0.33]).tolist()
        confidence_scores = np.clip(
            np.random.rand(num_samples, 1).tolist(),
            0.34, 1.0
        )
    return ModelResponse(
        predictions=predictions,
        confidence_scores=confidence_scores
    )


@app.post('/predict-hs', response_model=ModelResponse)
async def predict_hs(input_data: ModelInput):
    return generate_test_responses('high', len(input_data.features))


@app.post('/predict-ls', response_model=ModelResponse)
async def predict_ls(input_data: ModelInput):
    return generate_test_responses('low', len(input_data.features))
