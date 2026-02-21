import sqlite3
conn = sqlite3.connect("../finance.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS recurring (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT,
    category TEXT,
    price REAL,
    payment_method TEXT
);
""")
conn.commit()
conn.close()
print("✅ Recurring table created!")