from pathlib import Path

BASE_DIR = Path(__file__)

MODEL_FILENAME = "model/knn_predict_model.joblib"
SCALER_FILENAME = "model/scaler.joblib"
DATASET_FILENAME = "dataset/credit_risk_train.csv"
ENCODER_MAPS_JSON_FILENAME = "model/encoder.json"
METRICS_JSON_FILENAME = "model/metrics.json"

CREDIT_SCORE_LABELS = {
            0: "bajo",
            1: "medio",
            2: "alto"
        }


FIELD_LABELS_ES = {
    "credit_mix": "mezcla de crédito (Buena / Estándar / Mala)",
    "interest_rate": "tasa de interés",
    "payment_of_min_amount": "si paga el monto mínimo (Sí / No)",
    "num_credit_inquiries": "número de consultas de crédito realizadas",
    "delay_from_due_date": "días de atraso desde la fecha de vencimiento",
}

N_FEATURES = 5

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"
OLLAMA_MODEL_TEMPERATURE = 0.2

API_BASE_URL = "http://127.0.0.1:8000"