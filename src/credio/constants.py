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
N_FEATURES = 5