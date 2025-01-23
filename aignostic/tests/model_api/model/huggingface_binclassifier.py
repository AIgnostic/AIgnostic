from transformers import pipeline  # type: ignore
from fastapi import FastAPI, HTTPException
from aignostic.pydantic_models.data_models import DataSet

app = FastAPI()

# utilising hugging face high-level pipeline for sentiment analysis
pipe = pipeline("text-classification", model="siebert/sentiment-roberta-large-english")


@app.post("/predict")
def predict(dataset: DataSet):
    try:
        input_text = dataset.rows
        results = []
        for text in input_text:
            if len(text) != 1:
                raise HTTPException(status_code=400, detail="Input text must be a single string")
            else:
                results.append(pipe(text[0]))
                assert isinstance(text, list), "Input text must be encapsulated in a list"
        # Return the classification result
        return DataSet(column_names=["response"], rows=results)
    except Exception as e:
        # Handle exceptions and return an HTTP 500 error
        raise HTTPException(status_code=500, detail=str(e))
