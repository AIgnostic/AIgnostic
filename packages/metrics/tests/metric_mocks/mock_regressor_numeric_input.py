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

TEST_DATA_REGRESSION = DatasetResponse(
    features=[
        [1.0, 2.0, 1.5, 55.0],
    ],
    labels=[
        [1.3],
    ],
    group_ids=[0] * 4
)


@app.post('/predict-perfect-stability', response_model=ModelResponse)
async def predict_hs(input_data: DatasetResponse):
    return ModelResponse(
        predictions=TEST_DATA_REGRESSION.labels * len(input_data.features),
    )


@app.post('/predict-low-stability', response_model=ModelResponse)
async def predict_ls(input_data: DatasetResponse):
    return ModelResponse(
        predictions=[
            [random.uniform(-100, 100)]
            for _ in range(
                len(input_data.features)
            )
        ],
    )
