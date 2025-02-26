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


@app.post("/predict", response_model=LLMResponse)
def predict(input: LLMInput) -> LLMResponse:
    """
    Given a prompt, generate a *single token* and return the response.
    """
    # Tokenise the input prompt
    input_ids = tokenizer(input.prompt, return_tensors="pt").input_ids.to(model.device)

    # Generate only one token
    output = model.generate(
        input_ids,
        max_new_tokens=1,  # Single token generation
        do_sample=True,  # Enable sampling for diversity
        temperature=0.6,  # Control randomness
        top_p=0.9  # Top-p nucleus sampling
    )

    # Extract the newly generated token
    new_token_id = output[0][-1].item()
    new_token = tokenizer.decode(new_token_id, skip_special_tokens=True)

    return LLMResponse(response=new_token)  # Return only the generated single token


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5020)
