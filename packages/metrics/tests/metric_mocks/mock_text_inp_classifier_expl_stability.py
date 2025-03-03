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

TEST_INPUT_TEXT_CLASSIFICATION = ModelInput(
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

TEST_INPUT_NEXT_TOKEN_GENERATION = ModelInput(
    features=[
        ["How are you doing today?"],
        ["What is the weather like in London right now?"]
    ],
    labels=[
        ['I am doing well.'],
        ['It\'s raining - big surprise!']
    ],
    group_ids=[0] * 2
)


def generate_test_responses_text_classification(stability: str, num_samples: int):
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


def generate_test_responses_ntg(stability: str, num_samples: int):
    """
    Generate test responses for high or low stability

    :param stability: str ['high' or 'low'] - the stability of the model responses
    :param multiplier: int - the number of times to repeat the test input
    :return: ModelResponse - the model response object
    """
    predictions = []
    if stability == "high":
        predictions = [
            ['I am doing well.']
        ] * num_samples
    elif stability == "low":
        options = [
            'I', 'hello', 'weather', 'is', 'terrible', 'world', 'america', 'alan',
            'turing', 'apple', 'microsoft', 'bill', 'gates', 'car', 'house', 'dog',
            'cat', 'bird', 'plane', 'train', 'bus', 'subway', 'taxi', 'uber', 'lyft',
            'food', 'drink', 'water', 'soda', 'juice', 'milk', 'coffee', 'tea', 'beer',
            'germany', 'france', 'spain', 'italy', 'england', 'scotland', 'wales', 'ireland',
            'hot', 'cold', 'warm', 'freezing', 'boiling', 'cool', 'mild', 'moderate', 'extreme',
            'fast', 'slow', 'quick', 'rapid', 'speedy', 'leisurely', 'relaxed', 'calm',
            'peaceful', 'quiet', 'noisy', 'loud', 'silent', 'talkative', 'chatty', 'excited'
        ]
        output_lengths = np.random.randint(1, 20, size=num_samples)
        predictions = [
            [' '.join(np.random.choice(options, size=length))]
            for length in output_lengths
        ]
    return ModelResponse(
        predictions=predictions,
    )


@app.post('/predict-hs', response_model=ModelResponse)
async def predict_hs(input_data: ModelInput):
    return generate_test_responses_text_classification('high', len(input_data.features))


@app.post('/predict-ls', response_model=ModelResponse)
async def predict_ls(input_data: ModelInput):
    return generate_test_responses_text_classification('low', len(input_data.features))


@app.post('/predict-hs-ntg', response_model=ModelResponse)
async def predict_hs_ntg(input_data: ModelInput):
    return generate_test_responses_ntg('high', len(input_data.features))


@app.post('/predict-ls-ntg', response_model=ModelResponse)
async def predict_ls_ntg(input_data: ModelInput):
    return generate_test_responses_ntg('low', len(input_data.features))