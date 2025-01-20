from transformers import pipeline
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.testclient import TestClient

app = FastAPI()

# utilising hugging face high-level pipeline for sentiment analysis
pipe = pipeline("text-classification", model="siebert/sentiment-roberta-large-english")

# Define the input data model using Pydantic
class TextInput(BaseModel):
    text: str

@app.post("/predict")
def predict(input: TextInput):
    try:
        result = pipe(input.text)
        # Return the classification result
        return {"label": result[0]['label'], "score": result[0]['score']}
    except Exception as e:
        # Handle exceptions and return an HTTP 500 error
        raise HTTPException(status_code=500, detail=str(e))
