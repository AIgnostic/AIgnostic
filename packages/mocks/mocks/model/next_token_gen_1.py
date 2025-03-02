from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import torch.nn as nn
from common.models import ModelInput, ModelResponse

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
    messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]
    print("Messages: ")
    print(messages)

    # Tokenize and get input_ids and attention_mask
    tokenized_input = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(model.device)
    print("Passed tokeniszed input stage")
    input_ids = tokenized_input
    attention_mask = None

    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    print("Entering model generation")
    outputs = model.bfloat16().generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=256,
            do_sample=True,
            temperature=1.5,
            top_p=0.9,
        )
    print("Finished model generation")
    response = outputs[0][input_ids.shape[-1]:]
    new_token = tokenizer.decode(response, skip_special_tokens=True)
    predictions.append(new_token)
    confidence_scores.append(None)
    print("Predictions: ")
    print(predictions)
    return ModelResponse(predictions=predictions, confidence_scores=confidence_scores)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5020)
