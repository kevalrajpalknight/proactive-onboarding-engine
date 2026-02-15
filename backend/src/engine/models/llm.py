import os

from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI

load_dotenv()


llm = ChatOpenAI(
    model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)
