from langchain_ollama import ChatOllama

from credio.constants import OLLAMA_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL_TEMPERATURE

def get_chat_llm(temperature = None):
    """
    Crea un cliente de chat contra el modelo de Ollama configurado
    ("OLLAMA_MODEL", "OLLAMA_BASE_URL"). Permite sobrescribir la
    temperatura por defecto ("OLLAMA_MODEL_TEMPERATURE") para casos como
    la extracción estructurada, donde conviene una temperatura de 0.

    Args:
        temperature: temperatura a usar; si es None, se usa la del proyecto.

    Returns:
        ChatOllama listo para invocar.
    """
    return ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=OLLAMA_MODEL_TEMPERATURE if temperature is None else temperature
    )
