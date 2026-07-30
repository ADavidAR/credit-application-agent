import joblib
from pathlib import Path
import json

from credio.models import train_save_knn_model_scaler_encoder, train_save_decision_tree_model


class DecisionTreeService:
    """
    Servicio del modelo de árbol de decisión. Se encarga de cargar (o
    entrenar si no existe) el modelo, sus mapas de codificación y sus
    métricas, y de exponer la predicción de riesgo crediticio.
    """

    def __init__(self, model_path: str, encoder_maps_path: str, metrics_path: str):
        """
        Constructor.

        Args:
            model_path: ruta al modelo entrenado (.joblib).
            encoder_maps_path: ruta al JSON con los mapas de codificación.
            metrics_path: ruta al JSON con las métricas del modelo.
        """
        self.model = None
        self.encoder_maps = None
        self.metrics = None
        self.model_path = Path(model_path)
        self.encoder_maps_path = Path(encoder_maps_path)
        self.metrics_path = Path(metrics_path)

    def load_or_train(self) -> None:
        """
        Carga el modelo, los mapas de codificación y las métricas desde
        disco si ya existen; si falta alguno, entrena el árbol de decisión
        desde cero y guarda los nuevos artefactos.
        """
        if self.model_path.exists() and self.encoder_maps_path.exists() and self.metrics_path.exists():
            print(f"Cargando modelo existente desde: {self.model_path}")
            self.model = joblib.load(self.model_path)

            print(f"Cargando diccionario de codificación/decodificación existente desde: {self.encoder_maps_path}")
            with open(self.encoder_maps_path, "r", encoding="utf-8") as f:
                self.encoder_maps = json.load(f)

            print(f"Cargando metricas del modelo existente desde: {self.encoder_maps_path}")
            with open(self.metrics_path, "r", encoding="utf-8") as f:
                self.metrics = json.load(f)
        else:
            print(f"No se encontró alguno de los archivos:\n   {self.model_path}\n   {self.encoder_maps_path}\n   {self.metrics_path}")
            self.model, self.encoder_maps, self.metrics = train_save_decision_tree_model()

    def predict(self, features: list[float|int]) -> int:
        """
        Predice la clase de riesgo crediticio para un vector de features
        ya codificado, en el mismo orden usado durante el entrenamiento.

        Args:
            features: valores de las 15 variables del modelo, en orden.

        Returns:
            Clase predicha (0 = bajo, 1 = medio, 2 = alto).

        Raises:
            RuntimeError: si el modelo aún no fue cargado ni entrenado.
        """
        if self.model is None:
            raise RuntimeError("El modelo no ha sido cargado ni entrenado.")
        print([features])
        prediction = self.model.predict([features])
        print(prediction[0])
        return int(prediction[0])


class KNNService:
    """
    Servicio del modelo KNN. Se encarga de cargar (o entrenar si no
    existe) el modelo, su escalador, sus mapas de codificación y sus
    métricas, y de exponer la predicción de riesgo crediticio.
    """

    def __init__(self, model_path: str, scaler_path: str, encoder_maps_path: str, metrics_path: str):
        """
        Constructor.

        Args:
            model_path: ruta al modelo entrenado (.joblib).
            scaler_path: ruta al escalador ajustado (.joblib).
            encoder_maps_path: ruta al JSON con los mapas de codificación.
            metrics_path: ruta al JSON con las métricas del modelo.
        """
        self.model = None
        self.scaler = None
        self.encoder_maps = None
        self.metrics = None
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)
        self.encoder_maps_path = Path(encoder_maps_path)
        self.metrics_path = Path(metrics_path)

    def load_or_train(self) -> None:
        """
        Carga el modelo, el escalador, los mapas de codificación y las
        métricas desde disco si ya existen; si falta alguno, entrena el
        KNN desde cero y guarda los nuevos artefactos.
        """
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
        """
        Escala el vector de features y predice la clase de riesgo crediticio.

        Args:
            features: valores de las variables del modelo, en orden, sin escalar.

        Returns:
            Clase predicha (0 = bajo, 1 = medio, 2 = alto).

        Raises:
            RuntimeError: si el modelo aún no fue cargado ni entrenado.
        """
        if self.model is None:
            raise RuntimeError("El modelo no ha sido cargado ni entrenado.")

        scaled_features = self.scaler.transform([features])
        prediction = self.model.predict(scaled_features)
        return int(prediction[0])
