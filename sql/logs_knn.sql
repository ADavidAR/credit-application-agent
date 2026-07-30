DROP TABLE IF EXISTS Logs;

CREATE TABLE Logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credit_mix TEXT NOT NULL,
    interest_rate REAL NOT NULL,
    payment_of_min_amount TEXT NOT NULL,
    num_credit_inquiries INTEGER NOT NULL,
    delay_from_due_date INTEGER NOT NULL,
    credit_risk INTEGER NOT NULL,
    prediction_date TEXT DEFAULT (datetime('now', 'localtime'))
)