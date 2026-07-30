DROP TABLE IF EXISTS Logs;

CREATE TABLE Logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    outstanding_debt REAL NOT NULL,
    credit_mix TEXT NOT NULL,
    interest_rate REAL NOT NULL,
    credit_history_age INTEGER NOT NULL,
    delay_from_due_date INTEGER NOT NULL,
    credit_risk INTEGER NOT NULL,
    prediction_date TEXT DEFAULT (datetime('now', 'localtime'))
)