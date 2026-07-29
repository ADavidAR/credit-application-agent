from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException


from credio.services.prediction_models import DecisionTreeService
from credio.services.log import LogService
from src.credio.schemas import PredictionRequest
from src.credio.constants import ( MODEL_FILENAME, SCALER_FILENAME, ENCODER_MAPS_JSON_FILENAME,
                                    CREDIT_SCORE_LABELS, METRICS_JSON_FILENAME, DB_URL_TREE)

knn_service = DecisionTreeService(
    MODEL_FILENAME,
    ENCODER_MAPS_JSON_FILENAME,
    METRICS_JSON_FILENAME
)

log_service = LogService(DB_URL_TREE)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        knn_service.load_or_train()
    except Exception as e:
        print(f"Error crítico al inicializar el modelo: {e}")
        raise e
    
    yield
    knn_service.model = None
    knn_service.scaler = None
    knn_service.encoder_maps = None
    print("Modelo liberado de la memoria.")

app = FastAPI(
    title="API de riesgo crediticio",
    lifespan=lifespan
)

@app.post("/predict")
def predict_credit_risk(request: PredictionRequest):
    try:
        input_data = [

                request.monthly_inhand_salary,
                request.credit_history_age,
                request.total_emi_per_month,
                request.interest_rate,
                request.num_of_loan,
                request.delay_from_due_date,
                request.num_of_delayed_payment,
                request.num_credit_inquiries,
                knn_service.encoder_maps["credit_mix"].get( request.credit_mix ),
                request.outstanding_debt,
                knn_service.encoder_maps["payment_of_min_amount"].get( request.payment_of_min_amount ),
                request.credit_utilization_ratio,
                request.payment_of_min_amount,
                request.monthly_balance,
                knn_service.encoder_maps["spend_level"].get( request.spend_level ),
                knn_service.encoder_maps["value_level"].get( request.value_level )
        ]
        pred_risk = knn_service.predict(input_data)
        label = CREDIT_SCORE_LABELS.get(pred_risk, "Desconocido")

        log_service.add_log(request, pred_risk)
        return {
            "risk_level": label
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def get_metrics():
    return knn_service.metrics