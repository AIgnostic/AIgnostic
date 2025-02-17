from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app: FastAPI = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the mock server!"}


@app.post('/get-prediction-and-confidence')
async def get_prediction_and_confidence(input_data: dict):
    n = len(input_data["features"])
    predictions = [[random.randint(0, 1)] for _ in range(n)]
    confidence_scores = [[round(random.uniform(0.5, 1.0), 2)] for _ in range(n)]
    return {
        "predictions": predictions,
        "confidence_scores": confidence_scores,
    }
