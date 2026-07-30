from .llm_client import get_chat_llm
from .prompts import EXTRACTION_PROMPT, CONFIRMATION_INTENT_PROMPT
from credio.schemas import CollectedData, ConfirmationIntent


class DataExtractor:
    """
    Extractor de datos de la conversación. Usa el LLM en modo de salida
    estructurada para leer el historial de chat y devolver un "CollectedData"
    con los campos que el usuario ya haya proporcionado.
    """

    def __init__(self) -> None:
        self._llm = get_chat_llm(temperature = 0).with_structured_output(CollectedData)

    def extract(self, conversation_text: str) -> CollectedData:
        """
        Analiza el texto de la conversación y extrae los campos reconocidos.

        Args:
            conversation_text: transcripción de la conversación.

        Returns:
            CollectedData con los valores detectados. Los no mencionados quedan en null.
        """
        return self._llm.invoke(EXTRACTION_PROMPT.format(conversation=conversation_text))


class ConfirmationExtractor:
    """
    Clasificador de intención de confirmación. Usa el LLM en modo de salida
    estructurada para determinar si la respuesta del usuario confirma,
    rechaza o no aclara el resumen de datos que se le mostró.
    """

    def __init__(self) -> None:
        self._llm = get_chat_llm(temperature = 0).with_structured_output(ConfirmationIntent)

    def extract(self, user_message: str) -> ConfirmationIntent:
        """
        Clasifica la respuesta del usuario ante la solicitud de confirmación.

        Args:
            user_message: mensaje del usuario a interpretar.

        Returns:
            ConfirmationIntent con "confirmed" en True, False o null (ambiguo).
        """
        return self._llm.invoke(CONFIRMATION_INTENT_PROMPT.format(user_message=user_message))
