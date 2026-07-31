import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException


from credio.services.prediction_models import DecisionTreeService
from credio.services.log import LogService
from credio.schemas import PredictionRequest
from credio.constants import ( MODEL_FILENAME, ENCODER_MAPS_JSON_FILENAME,
                                    CREDIT_SCORE_LABELS, METRICS_JSON_FILENAME, DB_URL_TREE)

model_service = DecisionTreeService(
    MODEL_FILENAME,
    ENCODER_MAPS_JSON_FILENAME,
    METRICS_JSON_FILENAME
)

log_service = LogService(str(DB_URL_TREE))

logger = logging.getLogger("credio.api")


def _encode(field_name: str, value: str) -> int:
    """
    Codifica un valor categórico usando los mapas del modelo, validando
    que el valor sea reconocido en vez de dejarlo pasar como null.

    Args:
        field_name: nombre del campo categórico (clave en `encoder_maps`).
        value: valor recibido en la solicitud.

    Returns:
        Código entero correspondiente al valor.

    Raises:
        HTTPException: 422 si el valor no está en el mapa de codificación.
    """
    encoded = model_service.encoder_maps.get(field_name, {}).get(value)
    if encoded is None:
        raise HTTPException(
            status_code=422,
            detail=f"Valor no reconocido para '{field_name}': '{value}'.",
        )
    return encoded

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación FastAPI. Carga (o entrena si no existe)
    el modelo de riesgo crediticio al arrancar el servidor, y libera el
    modelo de memoria al apagarlo.

    Args:
        app: instancia de FastAPI a la que se asocia este ciclo de vida.
    """
    try:
        model_service.load_or_train()
    except Exception as e:
        print(f"Error crítico al inicializar el modelo: {e}")
        raise e
    
    yield
    model_service.model = None
    model_service.scaler = None
    model_service.encoder_maps = None
    print("Modelo liberado de la memoria.")

app = FastAPI(
    title="API de riesgo crediticio",
    lifespan=lifespan
)

@app.post("/predict")
def predict_credit_risk(request: PredictionRequest):
    """
    Calcula el nivel de riesgo crediticio de una solicitud. Codifica los
    campos categóricos con los mapas del modelo, delega la predicción al
    "DecisionTreeService", registra el resultado en el log correspondiente
    y devuelve la etiqueta de riesgo ("bajo", "medio" o "alto").

    Args:
        request: datos de la solicitud de crédito.

    Returns:
        dict con la clave "risk_level" y la etiqueta de riesgo obtenida.
    """
    try:
        input_data = [
                request.annual_income,
                request.monthly_inhand_salary,
                request.credit_history_age,
                request.total_emi_per_month,
                request.interest_rate,
                request.num_of_loan,
                request.delay_from_due_date,
                request.num_credit_inquiries,
                _encode("credit_mix", request.credit_mix),
                request.outstanding_debt,
                request.credit_utilization_ratio,
                _encode("payment_of_min_amount", request.payment_of_min_amount),
                request.monthly_balance,
                _encode("spend_level", request.spend_level),
                _encode("value_level", request.value_level)
        ]

        pred_risk = model_service.predict(input_data)
        label = CREDIT_SCORE_LABELS.get(pred_risk, "Desconocido")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo calcular el riesgo crediticio: {e}")

    try:
        log_service.add_log(request, pred_risk)
    except Exception:
        logger.exception("No se pudo guardar la predicción en la bitácora")

    return {
        "risk_level": label
    }

@app.get("/")
def get_metrics():
    return model_service.metrics