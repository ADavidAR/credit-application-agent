import joblib
from pathlib import Path
import json

from src.credio.model.build import train_save_knn_model_scaler_encoder
class KNNService:
    def __init__(self, model_path: str, scaler_path: str, encoder_maps_path: str):
        self.model = None
        self.scaler = None
        self.encoder_maps = None
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)
        self.encoder_maps_path = Path(encoder_maps_path)


    def load_or_train(self) -> None:
        if self.model_path.exists() and self.scaler_path.exists() and self.encoder_maps_path.exists():
            print(f"Cargando modelo existente desde: {self.model_path}")
            self.model = joblib.load(self.model_path)

            print(f"Cargando escalador existente desde: {self.scaler_path}")
            self.scaler = joblib.load(self.scaler_path)

            print(f"Cargando diccionario de codificación/decodificación existente desde: {self.encoder_maps_path}")
            with open(self.encoder_maps_path, "r", encoding="utf-8") as archivo:
                self.encoder_maps = json.load(archivo)
        else:
            print(f"No se encontró alguno de los archivos:\n   {self.model_path}\n   {self.scaler_path}\n   {self.encoder_maps_path}")
            self.model, self.scaler, self.encoder_maps = train_save_knn_model_scaler_encoder()

    def predict(self, features: list[float]) -> int:
        if self.model is None:
            raise RuntimeError("El modelo no ha sido cargado ni entrenado.")

        scaled_features = self.scaler.transform(features)
        prediction = self.model.predict([scaled_features])
        return int(prediction[0])