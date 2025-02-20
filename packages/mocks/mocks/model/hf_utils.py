from fastapi import HTTPException
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from common.models import ModelInput, ModelResponse
import torch


def predict(input: ModelInput, model_name: str) -> ModelResponse:
    try:
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        if not input.features:
            return ModelResponse(predictions=[], confidence_scores=[])

        # Convert nested list to list of strings
        texts = [" ".join(map(str, features)) for features in input.features]
        
        # Tokenize the input texts
        inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits

            # Apply softmax on output scores to get probabilities
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

            predicted_class_ids = logits.argmax(dim=-1).tolist()
            labels = [[model.config.id2label[class_id]] for class_id in predicted_class_ids]
            return ModelResponse(predictions=labels, confidence_scores=probabilities.tolist())
    except Exception as e:
        raise HTTPException(detail=f"Error occured during model prediction: {e}", status_code=400)
