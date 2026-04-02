import sqlite3

def init_db():
    conn = sqlite3.connect("meddesk.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients(
            policy_number TEXT PRIMARY KEY,
            name TEXT,
            plan_type TEXT,
            deductible_met REAL,
            last_service TEXT,
            last_service_date TEXT
        )
""" )

    conn.commit()
    conn.close()

def seed_db():
    conn = sqlite3.connect("meddesk.db")
    cursor = conn.cursor()
    patients = [
        ("SC-2024-001", "Jane Smith", "PPO", 800.00, "Emergency Medicine", "2026-01-01"),
        ("SC-2025-001", "John Doe", "HMO", 0.00, "Anesthesia", "2025-12-05"),
        ("SC-2024-002", "Maria Garcia", "PPO", 1500.00, "Hospital Medicine", "2025-11-20"),
        ("SC-2024-003", "James Lee", "EPO", 300.00, "Critical Care", "2026-02-14"),
    ]
    cursor.executemany("INSERT OR IGNORE INTO patients VALUES (?, ?, ?, ?, ?, ?)", patients)
    conn.commit()
    conn.close()

def get_patient(policy_number):
    conn = sqlite3.connect("meddesk.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE policy_number = ?", (policy_number,))
    row = cursor.fetchone()
    conn.close()
    return row

