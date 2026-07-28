DROP TABLE IF EXISTS Logs;

CREATE TABLE Logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annual_income REAL NOT NULL,
    monthly_inhand_salary REAL NOT NULL,
    credit_history_age INTEGER NOT NULL,
    total_emi_per_month REAL NOT NULL,
    interest_rate REAL NOT NULL,
    num_of_loan INTEGER NOT NULL,
    delay_from_due_date INTEGER NOT NULL,
    num_of_delayed_payment INTEGER NOT NULL,
    num_credit_inquiries INTEGER NOT NULL,
    credit_mix TEXT NOT NULL,
    outstanding_debt REAL NOT NULL,
    credit_utilization_ratio REAL NOT NULL,
    payment_of_min_amount TEXT NOT NULL,
    monthly_balance REAL NOT NULL,
    spend_level TEXT NOT NULL,
    value_level TEXT NOT NULL,
    credit_risk INTEGER NOT NULL,
    predict_date TEXT DEFAULT CURRENT_TIMESTAMP
)