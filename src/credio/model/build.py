import os

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.neighbors import KNeighborsClassifier 
from scipy.stats import zscore
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
import joblib

def build_knn_model():
    filename = "modelo_predictivo_knn.joblib"
    knn_model = train_knn_model()
    joblib.dump(knn_model, filename)
    print(f"Modelo KNN guardado en: {os.getcwd()}\\{filename}")

# Nota: codificación de "credit_score"
#     {
#         0: "Poor",
#         1: "Standard",
#         2: "Good",
#     }



def train_knn_model():
    df  = pd.read_csv("./dataset/credit_score_train.csv")

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
        "credit_score"  # TARGET
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
    nominal_cols = [c for c in cat_cols if c not in ordinal_cols and c != "credit_score"]
    df_selected["credit_mix"] = df_selected["credit_mix"].map(
        {
            'Good': 2,
            'Standard': 1,
            'Bad': 0
        }
    )

    df_selected["spend_level"] = df_selected["spend_level"].map(
        {
            'Low': 0,
            'High': 1
        }
    )

    df_selected["value_level"] = df_selected["value_level"].map(
        {
            'Small': 0, 
            'Medium': 1,
            'Large': 2
        }
    )

    encoder = OrdinalEncoder()
    df_selected[nominal_cols] = encoder.fit_transform(df_selected[nominal_cols])

    z_ = zscore(df_selected[num_cols])
    mask = (np.abs(z_) > 3).any(axis=1)
    df_cleaned = df_selected[~mask]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_cleaned.drop("credit_score", axis=1))
    y = df_cleaned["credit_score"]

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)

    candidate_k = round(np.sqrt(len(y_train)))
    optimal_k = candidate_k if candidate_k % 2 else candidate_k + 1 

    knn_model = KNeighborsClassifier(n_neighbors=optimal_k)

    knn_model.fit(X_train, y_train)

    y_pred = knn_model.predict(X_test)

    print("accuracy: ", accuracy_score(y_test, y_pred))
    print()
    print("report: ", classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred)

    print("cm: \n", cm)
    print()

    return knn_model
