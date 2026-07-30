import pandas as pd
import numpy as np
import json

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.neighbors import KNeighborsClassifier 
from scipy.stats import zscore
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from pathlib import Path
import joblib


from credio.constants import N_IMPORTANT_FEATURES, BASE_DIR, MODEL_FILENAME, SCALER_FILENAME, DATASET_FILENAME, ENCODER_MAPS_JSON_FILENAME, METRICS_JSON_FILENAME

def save_knn_model_scaler_encoder(knn_model, scaler, encoding_maps):
    """
    Persiste en disco los artefactos del modelo KNN entrenado: el modelo
    (".joblib"), el escalador (".joblib") y los mapas de codificación de
    variables categóricas (".json").

    Args:
        knn_model: modelo KNeighborsClassifier ya entrenado.
        scaler: StandardScaler ajustado usado para escalar las features.
        encoding_maps: mapas de codificación categórica a persistir.
    """
    Path(MODEL_FILENAME).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(knn_model, MODEL_FILENAME)
    print(f"Modelo KNN guardado en: {BASE_DIR / MODEL_FILENAME}")

    joblib.dump(scaler, SCALER_FILENAME)
    print(f"Escalador guardado en: {BASE_DIR / SCALER_FILENAME}")

    with open(ENCODER_MAPS_JSON_FILENAME, "w") as f:
        json.dump(encoding_maps, f, ensure_ascii=False, indent=4)

"""
    Nota: codificación de "credit_risk"
        {
            0: "low",
            1: "medium",
            2: "high",
        }
"""


def train_save_knn_model_scaler_encoder():
    """
    Entrena el modelo KNN de riesgo crediticio de punta a punta: carga el
    dataset, limpia valores nulos y outliers, codifica las variables
    categóricas, escala las features, busca el mejor valor de k por f1-score
    y guarda el modelo, el escalador, los mapas de codificación y las
    métricas resultantes.

    Returns:
        list con [modelo KNN, escalador, mapas de codificación, métricas].
    """
    df  = pd.read_csv(DATASET_FILENAME)

    selected_columns = [
        "annual_income",  # Ingreso anual bruto, indicador de capacidad de pago
        "monthly_inhand_salary",  # Salario neto mensual, mide liquidez real disponible
        "credit_history_age", # Antigüedad del historial crediticio en meses
        "total_emi_per_month",  # Cuotas mensuales fijas que ya paga el cliente
        "interest_rate", # Tasa de interés promedio aplicada a sus créditos
        "num_of_loan",  # Número de préstamos activos
        "delay_from_due_date",  # Días promedio de retraso en pagos
        "num_credit_inquiries",  # Número de consultas de crédito recientes
        "credit_mix",  # Diversidad y calidad de los tipos de crédito manejados
        "outstanding_debt", # Deuda pendiente total
        "credit_utilization_ratio",  # Porcentaje del crédito disponible que está usando
        "payment_of_min_amount",  # Si paga solo el monto mínimo requerido
        "payment_behaviour",  # Patrón de gasto y pago del cliente
        "monthly_balance", # Saldo promedio que le queda al final del mes
        "credit_risk"  # TARGET
    ]

    df_selected = df[selected_columns]

    # Separando "payment_behaviour" para procesar mejor el significado de la columna 
    df_selected[["spend_level", "value_level"]] = df_selected["payment_behaviour"].str.extract(
        r"(High|Low)_spent_(Small|Medium|Large)_value_payments"
    )

    df_selected = df_selected.drop(columns=["payment_behaviour"])

    num_cols = df_selected.select_dtypes(include=[np.number]).columns
    cat_cols = df_selected.select_dtypes(exclude=[np.number]).columns

    df_selected[num_cols] = df_selected[num_cols].fillna(df_selected[num_cols].mean())
    df_selected[cat_cols] = df_selected[cat_cols].fillna(df_selected[cat_cols].mode().iloc[0])

    ordinal_cols = ["credit_mix", "spend_level", "value_level"]
    nominal_cols = [c for c in cat_cols if c not in ordinal_cols and c != "credit_risk"]

    encoding_maps = {
        "credit_mix": {
            'Good': 2,
            'Standard': 1,
            'Bad': 0
        },

        "spend_level": {
            'Low': 0,
            'High': 1
        },

        "value_level": {
            'Small': 0, 
            'Medium': 1,
            'Large': 2
        }
    }


    df_selected["credit_mix"] = df_selected["credit_mix"].map(encoding_maps["credit_mix"])

    df_selected["spend_level"] = df_selected["spend_level"].map(encoding_maps["spend_level"])

    df_selected["value_level"] = df_selected["value_level"].map(encoding_maps["value_level"])

    encoder = OrdinalEncoder()
    df_selected[nominal_cols] = encoder.fit_transform(df_selected[nominal_cols])

    col_idx = list(encoder.feature_names_in_).index("payment_of_min_amount")

    categories_payment_of_min_amount = encoder.categories_[col_idx]
    mapping_payment_of_min_amount = {cat: code for code, cat in enumerate(categories_payment_of_min_amount)}

    encoding_maps["payment_of_min_amount"] = mapping_payment_of_min_amount

    z_ = zscore(df_selected[num_cols])
    mask = (np.abs(z_) > 3).any(axis=1)
    df_cleaned = df_selected[~mask]

    correlations_w_target = np.abs(df_selected.corr()["credit_risk"].drop("credit_risk")).sort_values(ascending=False)
    
    most_important_features = correlations_w_target.head(N_IMPORTANT_FEATURES).index
    print("Columnas con mayor correlación con el target: \n      ", most_important_features.tolist())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_cleaned.drop("credit_risk", axis=1))
    y = df_cleaned["credit_risk"]

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)

    candidate_upper_k = round(np.sqrt(len(y_train)))
    upper_bound_k = candidate_upper_k if candidate_upper_k % 2 else candidate_upper_k + 1 

    k_vals = range(1, upper_bound_k + 1, 2)
    f1_s = []

    for k in k_vals:
        model = KNeighborsClassifier(k)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        f1 = f1_score(y_test, y_pred, average="weighted")
        print(f"k: {k} -- f1: {f1}")
        f1_s.append(f1)

    index_optimal_k = max(range(len(f1_s)), key=f1_s.__getitem__)
    optimal_k = k_vals[index_optimal_k]

    knn_model = KNeighborsClassifier(n_neighbors=optimal_k)

    knn_model.fit(X_train, y_train)

    y_pred = knn_model.predict(X_test)

    print("report: \n", classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred)

    f1 = f1_score(y_test, y_pred, average="weighted")
    ac = accuracy_score(y_test, y_pred)

    metrics_dict = {
        "k": optimal_k,
        "f1_score": f1,
        "accuracy_score": ac
    }

    labels = ["Clase 0", "Clase 1", "Clase 2"]
    cm_df = pd.DataFrame(cm, index=[f"Real {l}" for l in labels], 
                            columns=[f"Pred {l}" for l in labels])
    print(cm_df)
    print()

    with open(METRICS_JSON_FILENAME, "w") as f:
        json.dump(metrics_dict, f, ensure_ascii=False, indent=4)
    
    save_knn_model_scaler_encoder(knn_model, scaler, encoding_maps)
    return [knn_model, scaler, encoding_maps, metrics_dict]

