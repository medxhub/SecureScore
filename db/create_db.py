import sqlite3

# Connect to the SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect('database.db')

# Create a cursor object
c = conn.cursor()

# Create a table for storing applicant information
c.execute('''
        PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE applicants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    dob TEXT,
    marital_status TEXT,
    education_level TEXT,
    credit_score REAL,
    income REAL,
    debt_to_income_ratio REAL,
    loan_amount REAL,
    loan_to_value_ratio REAL,
    employment_years INTEGER,
    risk_score REAL,
    risk_level TEXT
);
CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    , role TEXT DEFAULT 'user');

CREATE TABLE loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    applicant_id INTEGER,
    amount REAL,
    status TEXT CHECK(status IN ('approved', 'pending', 'rejected'))
);
DELETE FROM sqlite_sequence;
COMMIT;

)''')

# Commit the changes and close the connection
conn.commit()
conn.close()
