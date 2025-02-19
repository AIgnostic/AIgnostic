from fastapi import HTTPException
from transformers import pipeline
from common.models import ModelInput, ModelResponse


def predict(input: ModelInput, pipe: pipeline) -> ModelResponse:
    try:
        inputs = input.features
        results = []
        for data in inputs:
            if len(data) != 1:
                raise HTTPException(status_code=400, detail=f"Input text must be a single string. Got {data}")
            else:
                result = pipe(data[0])  # Perform prediction
                results.append([r['label'] for r in result])  # Extract the label from the result
                assert isinstance(data, list), "Input text must be encapsulated in a list"

        return ModelResponse(predictions=results)
    except Exception as e:
        raise HTTPException(detail=f"Error occured during model prediction: {e}", status_code=400)
