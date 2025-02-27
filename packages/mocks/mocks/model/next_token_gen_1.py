"""
Single Token Generation Model
"""
from fastapi import FastAPI
from pydantic import BaseModel
from common.models import LLMInput, LLMResponse
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load model and tokenizer
name = "neuralmagic/Llama-2-7b-chat-quantized.w8a8"
tokenizer = AutoTokenizer.from_pretrained(name)
model = AutoModelForCausalLM.from_pretrained(name)
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predict", response_model=ModelResponse)
def predict(input: ModelInput) -> ModelResponse:
    predictions = []
    confidence_scores = []

    for prompt in input.features:
        # Assume the prompt is a list with one string element 
        input_text= prompt[0]

        input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to(model.device)
        output = model.generate(
            input_ids,
            max_length=input.max_length,
            do_sample=True,
            temperature=0.6,
            top_p=0.9
        )

        new_token_id = output[0][-1].item()
        new_token = tokenizer.decode(new_token_id, skip_special_tokens=True)
        predictions.append(new_token)
        confidence_scores.append(None) # TODO: Placeholder value

    return ModelResponse(predictions=predictions, confidence_scores=confidence_scores)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5020)
