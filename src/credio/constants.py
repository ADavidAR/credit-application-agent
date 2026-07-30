import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

MODEL_FILENAME = BASE_DIR / "model/predict_model.joblib"
SCALER_FILENAME = BASE_DIR / "model/scaler.joblib"
DATASET_FILENAME = BASE_DIR / "dataset/credit_risk_train.csv"
ENCODER_MAPS_JSON_FILENAME = BASE_DIR / "model/encoder.json"
METRICS_JSON_FILENAME = BASE_DIR / "model/metrics.json"

CREDIT_SCORE_LABELS = {
            0: "bajo",
            1: "medio",
            2: "alto"
        }


FIELD_LABELS_ES = {
    "annual_income": "Ingreso anual bruto",
    "monthly_inhand_salary": "Salario neto mensual",
    "credit_history_age": "Antigüedad del historial crediticio en meses",
    "total_emi_per_month": "Total en cuotas mensuales fijas que ya paga",
    "interest_rate": "Tasa de interés",
    "num_of_loan": "Número de préstamos activos",
    "delay_from_due_date": "Días de atraso desde la fecha de vencimiento",
    "num_credit_inquiries": "Número de consultas de crédito realizadas",
    "credit_mix": "Mezcla de crédito",
    "outstanding_debt": "Deuda pendiente total",
    "credit_utilization_ratio": "Porcentaje del crédito disponible que se está usando",
    "payment_of_min_amount": "Si paga el monto mínimo de sus deudas",
    "monthly_balance": "Saldo promedio que le queda al final del mes",
    "spend_level": "Patrón de gasto",
    "value_level": "Patrón de pago",
}

N_IMPORTANT_FEATURES = 5

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")
OLLAMA_MODEL_TEMPERATURE = float(os.environ.get("OLLAMA_MODEL_TEMPERATURE", "0.2"))

API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")

DB_URL_KNN = BASE_DIR / "db/logs_knn.db"
DB_URL_TREE = BASE_DIR / "db/logs_tree.db"