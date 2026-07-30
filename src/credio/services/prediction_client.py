import requests

from credio.constants import API_BASE_URL
from credio.schemas import PredictionRequest, RiskLevel


class NotConfiguredPredictionClient():
    """
    Implementación por defecto de un cliente de predicción. Solo 
    avisa que falta conectar el modelo real de riesgo crediticio.
    """

    def predict(self, request: PredictionRequest) -> RiskLevel:
        """
        Args:
            request: datos de la solicitud (no se usan).

        Raises:
            NotImplementedError: siempre, ya que no hay modelo configurado.
        """
        raise NotImplementedError(
            "No hay un Modelo Predictivo configurado. Conecta aquí el cliente real "
            "del modelo externo que calcula el riesgo crediticio."
        )


class ApiPredictionClient():
    """
    Cliente que consume el endpoint "/predict" de la API de credio,
    la cual usa el modelo ya entrenado para calcular el riesgo crediticio.
    """

    def __init__(self, base_url: str = API_BASE_URL, timeout: float = 10.0) -> None:
        """
        Constructor.

        Args:
            base_url: URL base de la API de predicción.
            timeout: tiempo máximo de espera de la petición, en segundos.
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def predict(self, request: PredictionRequest) -> RiskLevel:
        """
        Envía la solicitud a la API y devuelve el nivel de riesgo calculado.

        Args:
            request: datos completos de la solicitud de crédito.

        Returns:
            Nivel de riesgo ("alto", "medio" o "bajo").
        """
        response = requests.post(
            f"{self._base_url}/predict",
            json=request.model_dump(),
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()["risk_level"]
