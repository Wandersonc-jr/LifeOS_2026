import sqlite3
import pandas as pd

DB_NAME = "finance.db"

def fix_expenses_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("🔧 Starting Database Repair...")

    # 1. LIFT: Get the existing data
    try:
        # We read whatever is currently there
        df = pd.read_sql("SELECT * FROM expenses", conn)
        print(f"✅ Extracted {len(df)} rows from the broken table.")
    except Exception as e:
        print(f"❌ Error reading table: {e}")
        return

    # 2. DESTROY: Drop the broken table
    cursor.execute("DROP TABLE IF EXISTS expenses")
    print("✅ Broken table deleted.")

    # 3. REBUILD: Create the correct table with ID
    # Note: We use the exact column names from your CSV (Capitalized) to match your DataFrame
    # This prevents the "Column not found" error during insertion
    cursor.execute("""
    CREATE TABLE expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT,
        Category TEXT,
        Item TEXT,
        Price REAL,
        'Payment Method' TEXT
    );
    """)
    print("✅ Correct table structure created (with 'id').")

    # 4. SHIFT: Insert the data back
    # We use 'append' this time, which respects the existing table structure (and the ID)
    try:
        df.to_sql("expenses", conn, if_exists="append", index=False)
        print(f"✅ Successfully restored {len(df)} rows.")
    except Exception as e:
        print(f"❌ Error restoring data: {e}")

    conn.commit()
    conn.close()
    print("🚀 Repair Complete. You can run the dashboard now.")

if __name__ == "__main__":
    fix_expenses_table()