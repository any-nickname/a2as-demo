from smolagents import LiteLLMModel, InferenceClientModel
from dotenv import load_dotenv
import os

load_dotenv()

model: LiteLLMModel | InferenceClientModel

model_provider = os.getenv("MODEL_PROVIDER")

if model_provider == 'local':
    model_id = os.getenv("LOCAL_MODEL_ID")
    api_base = os.getenv("LOCAL_API_URL")
    model = LiteLLMModel(model_id=model_id, api_base=api_base, api_key="not-needed")
elif model_provider == 'huggingface':
    token = os.getenv("HUGGING_FACE_TOKEN")
    model_id = os.getenv("HUGGING_FACE_MODEL_ID")
    model = InferenceClientModel(model_id=model_id, token=token)