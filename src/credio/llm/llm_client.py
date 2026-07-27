from langchain_ollama import ChatOllama

from src.credio.constants import OLLAMA_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL_TEMPERATURE

def get_chat_llm(temperature = None):
    return ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=OLLAMA_MODEL_TEMPERATURE if temperature is None else temperature
    )
