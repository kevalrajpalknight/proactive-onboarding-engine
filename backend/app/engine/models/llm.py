import os

from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI

load_dotenv()

print("Loading LLM configuration from .env file")
print(f"Using model: {os.getenv('OPENAI_MODEL_NAME', 'gpt-4')}")
print(f"Using API Key: {'set' if os.getenv('OPENAI_API_KEY') else 'not set'}")

llm = ChatOpenAI(
    model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)
