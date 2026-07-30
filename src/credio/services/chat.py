import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from requests.exceptions import RequestException

from credio.llm.extractor import DataExtractor, ConfirmationExtractor
from credio.llm.llm_client import get_chat_llm
from credio.services.prediction_client import ApiPredictionClient, NotConfiguredPredictionClient
from credio.llm.prompts import (
    SYSTEM_PROMPT,
    RECOMMENDATION_PROMPT,
    RECOMMENDATION_SYSTEM_PROMPT,
    LAST_USER_MESSAGE,
)
from credio.schemas import CollectedData
from credio.constants import FIELD_LABELS_ES

logger = logging.getLogger("credio.chat")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)


class CreditRiskChatService:
    def __init__(self, prediction_client: ApiPredictionClient = None) -> None:
        self._llm = get_chat_llm()
        self._extractor = DataExtractor()
        self._confirmation_extractor = ConfirmationExtractor()
        self._prediction_client = prediction_client or NotConfiguredPredictionClient()
        self._data = CollectedData()
        self._history = [SystemMessage(content=SYSTEM_PROMPT)]
        self._awaiting_confirmation = False

    @property
    def collected_data(self) -> CollectedData:
        return self._data

    def send(self, user_message: str) -> str:
        if self._awaiting_confirmation:
            return self._handle_confirmation(user_message)

        self._history.append(HumanMessage(content=user_message))
        self._update_collected_data()
        missing = self._data.missing_fields()
        if missing:
            history_without_last_message = self._history[:-1]
            user_msg_w_missing = LAST_USER_MESSAGE.format(missing=self._missing_fields_notice(missing), user_message=user_message)

            reply = self._llm.invoke([*history_without_last_message, HumanMessage(content=user_msg_w_missing)])
            reply_text = str(reply.content)
            self._history.append(AIMessage(content=reply_text))
            return reply_text
        return self._ask_confirmation()

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
        changes = {}

        for field, value in extracted.model_dump().items():
            if (current[field] is None and value is not None) or (current[field] != value and value is not None):
                changes[field] = (current[field], value)
                current[field] = value

        self._data = CollectedData(**current)
        logger.debug("extracted=%s", extracted.model_dump())
        if changes:
            logger.debug("changes=%s", changes)

    def _missing_fields_notice(self, missing: list[str]) -> str:
        return ", ".join(f"({FIELD_LABELS_ES[field]})" for field in missing)

    def _ask_confirmation(self) -> str:
        reply_text = (
            "Ya se recopilaron todos los datos necesarios. Este es el resumen:\n\n"
            f"{self._format_collected_data()}\n\n"
            "¿Son correctos estos datos? (sí/no)"
        )
        self._history.append(AIMessage(content=reply_text))
        self._awaiting_confirmation = True

        logger.info("confirmation_requested data=%s", self._data.model_dump())
        return reply_text

    def _handle_confirmation(self, user_message: str) -> str:
        self._history.append(HumanMessage(content=user_message))
        intent = self._confirmation_extractor.extract(user_message)
        logger.debug("confirmation_intent=%s user_message=%r", intent.confirmed, user_message)

        if intent.confirmed is True:
            self._awaiting_confirmation = False
            return self._run_prediction()

        if intent.confirmed is False:
            self._awaiting_confirmation = False
            reply_text = "Entendido, dime qué dato quieres corregir."
            self._history.append(AIMessage(content=reply_text))
            return reply_text

        reply_text = "No entendí tu respuesta. ¿Los datos que te mostré son correctos? (sí/no)"
        self._history.append(AIMessage(content=reply_text))
        return reply_text

    def _format_collected_data(self) -> str:
        return "\n".join(f"- {FIELD_LABELS_ES[field]}: {value}" for field, value in self._data.model_dump().items())

    def _run_prediction(self) -> str:
        request = self._data.to_prediction_request()
        logger.info("prediction_request=%s", request.model_dump())
        try:
            risk_level = self._prediction_client.predict(request)
            logger.info("risk_level=%s", risk_level)
        except NotImplementedError:
            return (
                "Ya cuento con todos los datos necesarios. La predicción de riesgo la calcula un modelo externo que aún no está conectado a este chat."
            )
        except RequestException:
            logger.exception("prediction_request_failed")
            return (
                "Ya cuento con todos los datos necesarios, pero no pude comunicarme con la API "
                "de predicción de riesgo. Verifica que el servicio esté corriendo e intenta de nuevo."
            )

        return self._generate_recommendation(risk_level)

    def _reset(self) -> None:
        self._history = [SystemMessage(content=SYSTEM_PROMPT)]
        self._data = CollectedData()
        self._awaiting_confirmation = False

    def _generate_recommendation(self, risk_level: str) -> str:
        conversation = [msg for msg in self._history if not isinstance(msg, SystemMessage)]
        prompt = RECOMMENDATION_PROMPT.format(risk_level=risk_level, user_data=self._format_collected_data())

        messages = [SystemMessage(content=RECOMMENDATION_SYSTEM_PROMPT), *conversation, HumanMessage(content=prompt)]

        response = self._llm.invoke(messages)
        recommendation_text = str(response.content)
        self._history.append(AIMessage(content=recommendation_text))

        self._reset()
        return recommendation_text
