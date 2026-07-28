from .llm_client import get_chat_llm
from .prompts import EXTRACTION_PROMPT
from src.credio.schemas import CollectedData


class DataExtractor:
    def __init__(self) -> None:
        self._llm = get_chat_llm(temperature = 0).with_structured_output(CollectedData)

    def extract(self, conversation_text: str) -> CollectedData:
        return self._llm.invoke(EXTRACTION_PROMPT.format(conversation=conversation_text))
