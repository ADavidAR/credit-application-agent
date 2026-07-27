import requests

from src.credio.constants import API_BASE_URL
from src.credio.schema import PredictionRequest, RiskLevel


class NotConfiguredPredictionClient():
    # Implementación por defecto: avisa que falta conectar el modelo real de predicción

    def predict(self, request: PredictionRequest) -> RiskLevel:
        raise NotImplementedError(
            "No hay un Modelo Predictivo configurado. Conecta aquí el cliente real "
            "del modelo externo que calcula el riesgo crediticio."
        )


class ApiPredictionClient():
    # Consume el endpoint POST /predict de la API, que a su vez usa el modelo KNN ya entrenado para calcular el riesgo.

    def __init__(self, base_url: str = API_BASE_URL, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def predict(self, request: PredictionRequest) -> RiskLevel:
        response = requests.post(
            f"{self._base_url}/predict",
            json=request.model_dump(),
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()["risk_level"]
