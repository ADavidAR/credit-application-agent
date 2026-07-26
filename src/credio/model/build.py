import pandas as pd
import numpy as np
import json

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.neighbors import KNeighborsClassifier 
from scipy.stats import zscore
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
import joblib

from src.credio.constants import N_FEATURES, BASE_DIR, MODEL_FILENAME, SCALER_FILENAME, DATASET_FILENAME, ENCODER_MAPS_JSON_FILENAME

def train_save_knn_model_scaler_encoder(knn_model, scaler, encoding_maps):
    joblib.dump(knn_model, MODEL_FILENAME)
    print(f"Modelo KNN guardado en: {BASE_DIR / MODEL_FILENAME}")

    joblib.dump(scaler, SCALER_FILENAME)
    print(f"Escalador guardado en: {BASE_DIR / SCALER_FILENAME}")

    with open(ENCODER_MAPS_JSON_FILENAME, "w") as f:
        json.dump(encoding_maps, f, ensure_ascii=False, indent=4)

# Nota: codificación de "credit_risk"
#     {
#         0: "low",
#         1: "medium",
#         2: "high",
#     }



def train_save_knn_model_scaler_encoder():
    df  = pd.read_csv(DATASET_FILENAME)

    selected_columns = [
        "age",   # Edad del cliente, relacionada con estabilidad financiera
        "occupation",  # Profesión, relacionadocon el nivel de ingresos y estabilidad laboral
        "annual_income",  # Ingreso anual bruto, indicador de capacidad de pago
        "monthly_inhand_salary",  # Salario neto mensual, mide liquidez real disponible
        "credit_history_age", # Antigüedad del historial crediticio en meses
        "total_emi_per_month",  # Cuotas mensuales fijas que ya paga el cliente
        "num_bank_accounts",  # Número de cuentas bancarias que posee
        "num_credit_card",   # Número de tarjetas de crédito que posee
        "interest_rate", # Tasa de interés promedio aplicada a sus créditos
        "num_of_loan",  # Número de préstamos activos
        "delay_from_due_date",  # Días promedio de retraso en pagos
        "num_of_delayed_payment",  # Número de pagos retrasados
        "changed_credit_limit",  # Cambio porcentual en el límite de crédito otorgado
        "num_credit_inquiries",  # Número de consultas de crédito recientes
        "credit_mix",  # Diversidad y calidad de los tipos de crédito manejados
        "outstanding_debt", # Deuda pendiente total
        "credit_utilization_ratio",  # Porcentaje del crédito disponible que está usando
        "payment_of_min_amount",  # Si paga solo el monto mínimo requerido
        "amount_invested_monthly",   # Monto que invierte mensualmente
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

    ordinal_encoding_maps = {
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
        },

        "credit_risk" : {
            0: "low",
            1: "medium",
            2: "high"
        }
    }


    df_selected["credit_mix"] = df_selected["credit_mix"].map(ordinal_encoding_maps["credit_mix"])

    df_selected["spend_level"] = df_selected["spend_level"].map(ordinal_encoding_maps["spend_level"])

    df_selected["value_level"] = df_selected["value_level"].map(ordinal_encoding_maps["value_level"])

    encoder = OrdinalEncoder()
    df_selected[nominal_cols] = encoder.fit_transform(df_selected[nominal_cols])

    z_ = zscore(df_selected[num_cols])
    mask = (np.abs(z_) > 3).any(axis=1)
    df_cleaned = df_selected[~mask]

    correlations_w_target = np.abs(df_selected.corr()["credit_risk"].drop("credit_risk")).sort_values(ascending=False)
    
    X_cols = correlations_w_target.head(N_FEATURES).index
    print(X_cols)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_cleaned[X_cols])
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

    labels = ["Clase 0", "Clase 1", "Clase 2"]
    cm_df = pd.DataFrame(cm, index=[f"Real {l}" for l in labels], 
                            columns=[f"Pred {l}" for l in labels])
    print(cm_df)
    print()
    train_save_knn_model_scaler_encoder(knn_model, scaler, ordinal_encoding_maps)
    return [knn_model, scaler, ordinal_encoding_maps]
