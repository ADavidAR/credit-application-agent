from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from requests.exceptions import RequestException

from credio.llm.extractor import DataExtractor
from credio.llm.llm_client import get_chat_llm
from credio.models.prediction_client import ApiPredictionClient, NotConfiguredPredictionClient
from credio.llm.prompts import SYSTEM_PROMPT, RECOMMENDATION_PROMPT, RECOMMENDATION_SYSTEM_PROMPT
from credio.schemas import CollectedData
from credio.constants import FIELD_LABELS_ES

class CreditRiskChatService:
    def __init__(self, prediction_client: ApiPredictionClient = None) -> None:
        self._llm = get_chat_llm()
        self._extractor = DataExtractor()
        self._prediction_client = prediction_client or NotConfiguredPredictionClient()
        self._history = [SystemMessage(content=SYSTEM_PROMPT)]
        self._data = CollectedData()

    @property
    def collected_data(self) -> CollectedData:
        return self._data

    def send(self, user_message: str) -> str:
        self._history.append(HumanMessage(content=user_message))
        self._update_collected_data()

        reply = self._llm.invoke(self._history)
        reply_text = str(reply.content)
        self._history.append(AIMessage(content=reply_text))

        missing = self._data.missing_fields()
        if missing:
            return f"{reply_text}\n\n{self._missing_fields_notice(missing)}"

        return f"{reply_text}\n\n{self._run_prediction()}"

    def _render_conversation(self) -> str:
        lines = []
        for msg in self._history:
            if isinstance(msg, HumanMessage):
                lines.append(f"Usuario: {msg.content}")
            elif isinstance(msg, AIMessage):
                lines.append(f"Asistente: {msg.content}")
        return "\n".join(lines)

    def _update_collected_data(self) -> None:
        extracted = self._extractor.extract(self._render_conversation())
        current = self._data.model_dump()

        for field, value in extracted.model_dump().items():
            if current[field] is None and value is not None:
                current[field] = value

        self._data = CollectedData(**current)

    def _missing_fields_notice(self, missing: list[str]) -> str:
        labels = "- ".join(FIELD_LABELS_ES[field] for field in missing)
        return f"Nota: aún necesito estos datos para poder evaluar el riesgo: {labels}."

    def _run_prediction(self) -> str:
        request = self._data.to_prediction_request()
        try:
            risk_level = self._prediction_client.predict(request)
        except NotImplementedError:
            return (
                "Ya cuento con todos los datos necesarios. La predicción de riesgo la calcula un modelo externo que aún no está conectado a este chat."
            )
        except RequestException:
            return (
                "Ya cuento con todos los datos necesarios, pero no pude comunicarme con la API "
                "de predicción de riesgo. Verifica que el servicio esté corriendo e intenta de nuevo."
            )

        return self._generate_recommendation(risk_level)

    def _reset(self):
        self._history = [SystemMessage(content=SYSTEM_PROMPT)]
        self._data = CollectedData()

    def _generate_recommendation(self, risk_level: str) -> str:
        conversation = [msg for msg in self._history if not isinstance(msg, SystemMessage)]
        prompt = RECOMMENDATION_PROMPT.format(risk_level=risk_level)
        messages = [SystemMessage(content=RECOMMENDATION_SYSTEM_PROMPT), *conversation, HumanMessage(content=prompt)]

        response = self._llm.invoke(messages)
        recommendation_text = str(response.content)
        self._history.append(AIMessage(content=recommendation_text))

        self._reset()
        return recommendation_text
    
