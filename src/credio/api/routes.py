from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

import json

from src.credio.services.knn import KNNService
from src.credio.constants import MODEL_FILENAME, SCALER_FILENAME, ENCODER_MAPS_JSON_FILENAME, CREDIT_SCORE_LABELS, METRICS_JSON_FILENAME
from src.credio.schema import PredictionRequest

knn_service = KNNService(
    MODEL_FILENAME, 
    SCALER_FILENAME, 
    ENCODER_MAPS_JSON_FILENAME,
    METRICS_JSON_FILENAME
)

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
                knn_service.encoder_maps["credit_mix"].get((request.credit_mix)),
                request.interest_rate,
                knn_service.encoder_maps["payment_of_min_amount"].get(request.payment_of_min_amount),
                request.num_credit_inquiries,
                request.delay_from_due_date
        ]
        pred_class = knn_service.predict(input_data)
        label = CREDIT_SCORE_LABELS.get(pred_class, "Desconocido")
        
        return {
            "risk_level": label
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def get_metrics():
    return knn_service.metrics