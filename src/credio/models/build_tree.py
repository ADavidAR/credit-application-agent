import pandas as pd
import numpy as np
import json

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier 
from scipy.stats import zscore
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from pathlib import Path
import joblib


from credio.constants import N_IMPORTANT_FEATURES, BASE_DIR, MODEL_FILENAME, SCALER_FILENAME, DATASET_FILENAME, ENCODER_MAPS_JSON_FILENAME, METRICS_JSON_FILENAME

def save_tree_model_encoder(knn_model, encoding_maps):
    Path(MODEL_FILENAME).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(knn_model, MODEL_FILENAME)
    print(f"Modelo de Arbol de decisión guardado en: {BASE_DIR / MODEL_FILENAME}")

    with open(ENCODER_MAPS_JSON_FILENAME, "w") as f:
        json.dump(encoding_maps, f, ensure_ascii=False, indent=4)

# Nota: codificación de "credit_risk"
#     {
#         0: "low",
#         1: "medium",
#         2: "high",
#     }


def train_save_decision_tree_model():
    df  = pd.read_csv(DATASET_FILENAME)

    selected_columns = [
        "annual_income",  # Ingreso anual bruto, indicador de capacidad de pago
        "monthly_inhand_salary",  # Salario neto mensual, mide liquidez real disponible
        "credit_history_age", # Antigüedad del historial crediticio en meses
        "total_emi_per_month",  # Cuotas mensuales fijas que ya paga el cliente
        "interest_rate", # Tasa de interés promedio aplicada a sus créditos
        "num_of_loan",  # Número de préstamos activos
        "delay_from_due_date",  # Días promedio de retraso en pagos
        "num_of_delayed_payment",  # Número de pagos retrasados
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

    X = df_cleaned.drop("credit_risk", axis=1)
    y = df_cleaned["credit_risk"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    depths = range(3, 100, 2)
    f1_s = []

    for d in depths:
        model = DecisionTreeClassifier(max_depth=d, criterion="gini")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        f1 = f1_score(y_test, y_pred, average="weighted")
        print(f"{d} -> {f1}")
        f1_s.append(f1)

    index_optimal_depth = max(range(len(f1_s)), key=f1_s.__getitem__)
    optimal_depth = depths[index_optimal_depth]

    tree_model = DecisionTreeClassifier(n_neighbors=optimal_depth, criterion="gini")

    tree_model.fit(X_train, y_train)

    most_important_features = pd.DataFrame(
        {
            "feature": df_cleaned.drop("credit_risk", axis=1).columns,
            "importance": tree_model.feature_importances_
        }
    ).sort_values(by="importance", ascending=False).head(N_IMPORTANT_FEATURES)["feature"].tolist()

    print("Columnas con mayor correlación con el target: \n      ", most_important_features)
    y_pred = tree_model.predict(X_test)

    print("report: \n", classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred)

    f1 = f1_score(y_test, y_pred, average="weighted")
    ac = accuracy_score(y_test, y_pred)

    metrics_dict = {
        "depth": optimal_depth,
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
    
    # save_knn_model_scaler_encoder(tree_model, scaler, encoding_maps)
    save_tree_model_encoder(tree_model, encoding_maps)
    return [tree_model, encoding_maps, metrics_dict]
