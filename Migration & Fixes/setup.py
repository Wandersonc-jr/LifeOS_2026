import sqlite3
conn = sqlite3.connect("../finance.db")
cursor = conn.cursor()
cursor.execute('ALTER TABLE incomes ADD COLUMN paid INTEGER DEFAULT 1')
conn.commit()
conn.close()
print("✅ Recurring table created!")
