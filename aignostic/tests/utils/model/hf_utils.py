from fastapi import HTTPException
from transformers import pipeline
from aignostic.pydantic_models.data_models import ModelInput, ModelResponse


def predict(input: ModelInput, pipe: pipeline) -> ModelResponse:
    try:
        inputs = input.features
        results = []
        for data in inputs:
            if len(data) != 1:
                raise HTTPException(status_code=400, detail="Input text must be a single string")
            else:
                results.append(pipe(data[0]))  # Get string from singleton list
                assert isinstance(data, list), "Input text must be encapsulated in a list"
        return ModelResponse(predictions=results)
    except Exception as e:
        raise HTTPException(detail=f"Error occured during model prediction: {e}", status_code=400)
