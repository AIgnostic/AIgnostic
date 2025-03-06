import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from common.models import DatasetResponse, ModelResponse
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# CORS setup (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')


def list_available_gemini_models():
    try:
        for model in genai.list_models():
            print(f"Model: {model.name}")
            print(f"  Description: {model.description}")
            print(f"  Supported methods: {model.supported_generation_methods}")
    except Exception as e:
        print(f"Error listing models: {e}")


@app.post("/predict", response_model=ModelResponse)
async def predict(request: DatasetResponse):
    """Generates text using Gemini to complete an answer."""
    try:
        predictions = []
        for prompt in request.features:
            print(f"Prompt: {prompt}")
            response = model.generate_content(prompt)
            print(f"Response: {response.text}")
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                raise HTTPException(
                    status_code=400,
                    detail=f"Gemini blocked the prompt due to: {response.prompt_feedback.block_reason}"
                )
            predictions.append([response.text])
        print("Reached this")
        return ModelResponse(predictions=predictions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5030)