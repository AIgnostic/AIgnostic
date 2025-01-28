from transformers import pipeline
from fastapi import FastAPI, HTTPException
from aignostic.pydantic_models.data_models import ModelInput, ModelResponse

app = FastAPI()

# utilising hugging face high-level pipeline for sentiment analysis
pipe = pipeline("text-classification", model="siebert/sentiment-roberta-large-english")


@app.post("/predict", response_model=ModelResponse)
def predict(input: ModelInput) -> ModelResponse:
    try:
        input_text = input.features
        results = []
        for text in input_text:
            if len(text) != 1:
                raise HTTPException(status_code=400, detail="Input text must be a single string")
            else:
                assert isinstance(text, list), "Input text must be encapsulated in a list"
                results.append(pipe(text[0])) # Get string from singleton list
        # Return the classification result
        return ModelResponse(predictions=results)
    except Exception as e:
        # Handle exceptions and return an HTTP 500 error
        raise HTTPException(detail=f"Error occured during model prediction: {e}", status_code=500)
