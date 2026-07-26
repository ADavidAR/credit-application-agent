from pathlib import Path

BASE_DIR = Path(__file__)

MODEL_FILENAME = "model/knn__predict_model.joblib"
SCALER_FILENAME = "model/scaler.joblib"
DATASET_FILENAME = "dataset/credit_risk_train.csv"

N_FEATURES = 5