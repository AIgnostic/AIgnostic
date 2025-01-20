from transformers import pipeline
from fastapi import FastAPI, HTTPException, Query
from aignostic.pydantic_models.models import Data
from fastapi.testclient import TestClient

app = FastAPI()

# utilising hugging face high-level pipeline for sentiment analysis
pipe = pipeline("text-classification", model="siebert/sentiment-roberta-large-english")

@app.post("/predict")
def predict(dataset: Data):
    try:
        input_text = dataset.rows
        results = []
        for text in input_text:
            if len(text) != 1:
                raise HTTPException(status_code=400, detail="Input text must be a single string")
            else:
                results.append(pipe(text[0]))
                assert type(text) == list, "Input text must be encapsulated in a list"
        # Return the classification result
        return Data(column_names=["response"], rows=results)
    except Exception as e:
        # Handle exceptions and return an HTTP 500 error
        raise HTTPException(status_code=500, detail=str(e))
