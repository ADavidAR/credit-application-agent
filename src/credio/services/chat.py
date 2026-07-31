import logging

import httpx
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from ollama import ResponseError as OllamaResponseError
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
    """
    Servicio del chat de evaluación de riesgo crediticio. Mantiene el
    historial de la conversación y los datos recopilados, coordina la
    extracción de campos, el paso de confirmación previo a predecir, la
    llamada al "PredictionClient" y la redacción final de la recomendación.
    """

    def __init__(self, prediction_client: ApiPredictionClient = None) -> None:
        """
        Constructor.

        Args:
            prediction_client: cliente usado para calcular el riesgo; si no
                se indica, se usa "NotConfiguredPredictionClient".
        """
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
        """
        Procesa un mensaje del usuario y devuelve la respuesta del asistente.
        Si hay una confirmación pendiente, la resuelve; si no, actualiza los
        datos recopilados y, según falten o no campos, pide lo que falta o
        pasa al paso de confirmación previo a la predicción.

        Args:
            user_message: mensaje escrito por el usuario.

        Returns:
            Texto de respuesta para mostrarle al usuario.
        """
        try:
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
        except httpx.ConnectError:
            logger.exception("ollama_unreachable")
            return (
                "No pude conectarme con el modelo de lenguaje (Ollama). Verifica que esté corriendo e intenta de nuevo."
            )
        except OllamaResponseError as e:
            logger.exception("ollama_model_error")
            return (
                f"El modelo de lenguaje configurado no está disponible en Ollama ({e}). Verifica que esté descargado (`ollama pull <modelo>`)."
            )

    def _render_conversation(self) -> str:
        """
        Convierte el historial de mensajes en una transcripción de texto
        plano ("Usuario: ..." / "Asistente: ...") para pasarla al extractor.

        Returns:
            Transcripción de la conversación acumulada hasta ahora.
        """
        lines = []
        for msg in self._history:
            if isinstance(msg, HumanMessage):
                lines.append(f"Usuario: {msg.content}")
            elif isinstance(msg, AIMessage):
                lines.append(f"Asistente: {msg.content}")
        return "\n".join(lines)

    def _update_collected_data(self) -> None:
        """
        Vuelve a extraer los datos de toda la conversación y actualiza
        "self._data" con los valores nuevos o modificados (permite que el
        usuario corrija un dato ya dado). Registra en el log tanto lo
        extraído como los cambios aplicados, para poder auditar el proceso.
        """
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
        """
        Arma el mensaje de confirmación con el resumen de todos los datos
        recopilados y marca la sesión como en espera de esa confirmación.
        El texto se construye directo en código para que nunca pueda incluir 
        una evaluación de riesgo inventada.

        Returns:
            Texto de confirmación para mostrarle al usuario.
        """
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
        """
        Interpreta la respuesta del usuario a la solicitud de confirmación.
        Si confirma, dispara la predicción; si la rechaza, le pide que
        indique qué corregir; si la respuesta es ambigua, vuelve a preguntar.

        Args:
            user_message: respuesta del usuario a la confirmación pendiente.

        Returns:
            Texto de respuesta para mostrarle al usuario.
        """
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
        """
        Construye el "PredictionRequest" a partir de los datos ya
        confirmados y lo envía al "PredictionClient". Si el cliente no está
        configurado o la API no responde, devuelve un mensaje explicando
        el problema.

        Returns:
            Texto de respuesta con la recomendación final, o un aviso de error.
        """
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
        """Reinicia historial y datos recopilados tras completar una evaluación."""
        self._history = [SystemMessage(content=SYSTEM_PROMPT)]
        self._data = CollectedData()
        self._awaiting_confirmation = False

    def _generate_recommendation(self, risk_level: str) -> str:
        """
        Redacta el mensaje final para el usuario a partir del nivel de
        riesgo ya calculado por el modelo externo, y reinicia la sesión
        para permitir una nueva evaluación.

        Args:
            risk_level: nivel de riesgo ("alto", "medio" o "bajo") devuelto por la API.

        Returns:
            Texto de la recomendación final.
        """
        conversation = [msg for msg in self._history if not isinstance(msg, SystemMessage)]
        prompt = RECOMMENDATION_PROMPT.format(risk_level=risk_level, user_data=self._format_collected_data())

        messages = [SystemMessage(content=RECOMMENDATION_SYSTEM_PROMPT), *conversation, HumanMessage(content=prompt)]

        response = self._llm.invoke(messages)
        recommendation_text = str(response.content)
        self._history.append(AIMessage(content=recommendation_text))

        self._reset()
        return recommendation_text
