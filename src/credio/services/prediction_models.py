import joblib
from pathlib import Path
import json

from src.credio.models import train_save_knn_model_scaler_encoder, train_save_decision_tree_model


class DecisionTreeService:
    def __init__(self, model_path: str, encoder_maps_path: str, metrics_path: str):
        self.model = None
        self.encoder_maps = None
        self.metrics = None
        self.model_path = Path(model_path)
        self.encoder_maps_path = Path(encoder_maps_path)
        self.metrics_path = Path(metrics_path)


    def load_or_train(self) -> None:
        if self.model_path.exists() and self.scaler_path.exists() and self.encoder_maps_path.exists() and self.metrics_path.exists():
            print(f"Cargando modelo existente desde: {self.model_path}")
            self.model = joblib.load(self.model_path)

            print(f"Cargando diccionario de codificación/decodificación existente desde: {self.encoder_maps_path}")
            with open(self.encoder_maps_path, "r", encoding="utf-8") as f:
                self.encoder_maps = json.load(f)

            print(f"Cargando metricas del modelo existente desde: {self.encoder_maps_path}")
            with open(self.metrics_path, "r", encoding="utf-8") as f:
                self.metrics = json.load(f)
        else:
            print(f"No se encontró alguno de los archivos:\n   {self.model_path}\n   {self.scaler_path}\n   {self.encoder_maps_path}")
            self.model, self.encoder_maps, self.metrics = train_save_decision_tree_model()

    def predict(self, features: list[float|int]) -> int:
        if self.model is None:
            raise RuntimeError("El modelo no ha sido cargado ni entrenado.")
        prediction = self.model.predict([features])
        return int(prediction[0])


class KNNService:
    def __init__(self, model_path: str, scaler_path: str, encoder_maps_path: str, metrics_path: str):
        self.model = None
        self.scaler = None
        self.encoder_maps = None
        self.metrics = None
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)
        self.encoder_maps_path = Path(encoder_maps_path)
        self.metrics_path = Path(metrics_path)


    def load_or_train(self) -> None:
        if self.model_path.exists() and self.scaler_path.exists() and self.encoder_maps_path.exists() and self.metrics_path.exists():
            print(f"Cargando modelo existente desde: {self.model_path}")
            self.model = joblib.load(self.model_path)

            print(f"Cargando escalador existente desde: {self.scaler_path}")
            self.scaler = joblib.load(self.scaler_path)

            print(f"Cargando diccionario de codificación/decodificación existente desde: {self.encoder_maps_path}")
            with open(self.encoder_maps_path, "r", encoding="utf-8") as f:
                self.encoder_maps = json.load(f)

            print(f"Cargando metricas del modelo existente desde: {self.encoder_maps_path}")
            with open(self.metrics_path, "r", encoding="utf-8") as f:
                self.metrics = json.load(f)
        else:
            print(f"No se encontró alguno de los archivos:\n   {self.model_path}\n   {self.scaler_path}\n   {self.encoder_maps_path}")
            self.model, self.scaler, self.encoder_maps, self.metrics = train_save_knn_model_scaler_encoder()

    def predict(self, features: list[float|int]) -> int:
        if self.model is None:
            raise RuntimeError("El modelo no ha sido cargado ni entrenado.")

        scaled_features = self.scaler.transform([features])
        prediction = self.model.predict(scaled_features)
        return int(prediction[0])