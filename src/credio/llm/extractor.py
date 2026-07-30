from .llm_client import get_chat_llm
from .prompts import EXTRACTION_PROMPT, CONFIRMATION_INTENT_PROMPT
from credio.schemas import CollectedData, ConfirmationIntent


class DataExtractor:
    def __init__(self) -> None:
        self._llm = get_chat_llm(temperature = 0).with_structured_output(CollectedData)

    def extract(self, conversation_text: str) -> CollectedData:
        return self._llm.invoke(EXTRACTION_PROMPT.format(conversation=conversation_text))


class ConfirmationExtractor:
    def __init__(self) -> None:
        self._llm = get_chat_llm(temperature = 0).with_structured_output(ConfirmationIntent)

    def extract(self, user_message: str) -> ConfirmationIntent:
        return self._llm.invoke(CONFIRMATION_INTENT_PROMPT.format(user_message=user_message))
