from fastapi import HTTPException
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    AutoModelForCausalLM
)
from common.models import DatasetResponse, ModelResponse
import torch
# Load model directly


def predict_t2class(
    input: DatasetResponse,
    model_name: str,
    tokenizer_name: str = None,
    max_length: int = None
) -> ModelResponse:
    """
    Default predict function for text classification models from huggingface.

    :param: input: DatasetResponse object containing input features
    :param: model_name: Name of the model to be used for prediction
    :param: tokenizer_name = None: Name of the tokenizer to be used for tokenization.
        If not provided, the model_name is used to load the tokenizer.
    :param: max_length = None: Maximum length of the input sequence. If not provided,
        the maximum length supported by the model is used.

    :return: ModelResponse object containing predictions and confidence scores
    """
    try:
        if not input.features:
            return ModelResponse(predictions=[], confidence_scores=[])

        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_name if tokenizer_name else model_name
        )

        # Convert nested list to list of strings
        texts = [" ".join(map(str, features)) for features in input.features]

        # Tokenize the input texts
        inputs = tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=max_length
        )

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


def predict_causal_LM(
    input: DatasetResponse,
    model_name: str,
    tokenizer_name: str = None,
    max_length: int = None,
    num_beams: int = 1,
) -> ModelResponse:
    """
    Default predict function for causal language models from huggingface.

    :param: input: DatasetResponse object containing input features
    :param: model_name: Name of the model to be used for prediction
    :param: tokenizer_name = None: Name of the tokenizer to be used for tokenization.
        If not provided, the model_name is used to load the tokenizer.
    :param: max_length = None: Maximum length of the input sequence. If not provided,
        the maximum length supported by the model is used.
    :param: num_beams = 1: Number of beams to be used for beam search. If not provided,
        beam search is disabled.

    :return: ModelResponse object containing predictions
    """
    try:
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_name if tokenizer_name else model_name,
            padding_side="left"
        )
        print("Reached here - start of predict_causal_LM")
        # Convert nested list to list of strings
        texts = [" ".join(map(str, features)) for features in input.features]

        # Tokenize the input texts
        if not tokenizer.pad_token:
            tokenizer.pad_token = tokenizer.eos_token
        print(f"Converted input texts into token IDs: {texts}")
        inputs = tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=max_length
        )
        print(f"Tokenized input: {inputs}")
        # with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            num_beams=num_beams,
        )
        print(f"Generated outputs: {outputs}")
        # Decode the generated tokens
        one_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Decoded generated text: {one_text}")
        generated_texts = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        print(f"Decoded generated texts: {generated_texts}")
        return ModelResponse(predictions=[[text] for text in generated_texts])
    except Exception as e:
        raise HTTPException(detail=f"Error occured during model prediction: {e}", status_code=400)