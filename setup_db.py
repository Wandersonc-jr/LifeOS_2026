import sqlite3
import pandas as pd
import os

# --- CONFIGURATION ---
DB_NAME = "finance.db"
CSV_FILES = {
    "expenses": "finance.csv",
    "incomes": "incomes.csv",
    "cards": "cards.csv"
}


def create_connection():
    """Connect to the SQLite database (or create it if it doesn't exist)."""
    conn = sqlite3.connect(DB_NAME)
    return conn


def create_tables(conn):
    """Create the 3 necessary tables using SQL."""
    cursor = conn.cursor()

    # 1. EXPENSES TABLE
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS expenses
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       date
                       TEXT
                       NOT
                       NULL,
                       category
                       TEXT,
                       item
                       TEXT,
                       price
                       REAL,
                       payment_method
                       TEXT
                   );
                   """)

    # 2. INCOMES TABLE
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS incomes
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       date
                       TEXT
                       NOT
                       NULL,
                       category
                       TEXT,
                       item
                       TEXT,
                       price
                       REAL
                   );
                   """)

    # 3. CARDS TABLE
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS cards
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       card_name
                       TEXT
                       UNIQUE,
                       closing_day
                       INTEGER,
                       due_day
                       INTEGER
                   );
                   """)

    conn.commit()
    print("✅ Tables created successfully.")


def migrate_csv_to_sql(conn):
    """Read CSV files and insert data into SQL."""

    # --- MIGRATE EXPENSES ---
    if os.path.exists(CSV_FILES["expenses"]):
        df = pd.read_csv(CSV_FILES["expenses"])
        # Rename columns to match SQL (lowercase, no spaces) if necessary
        # We assume your CSV headers are: Date, Category, Item, Price, Payment Method
        # We need to ensure column order matches or use pandas to_sql

        # Simpler way: Use pandas magic
        df.to_sql("expenses", conn, if_exists="replace", index=False)
        print(f"✅ Migrated {len(df)} expenses.")
    else:
        print("⚠️ No finance.csv found. Table 'expenses' is empty.")

    # --- MIGRATE INCOMES ---
    if os.path.exists(CSV_FILES["incomes"]):
        df = pd.read_csv(CSV_FILES["incomes"])
        df.to_sql("incomes", conn, if_exists="replace", index=False)
        print(f"✅ Migrated {len(df)} incomes.")
    else:
        print("⚠️ No incomes.csv found. Table 'incomes' is empty.")

    # --- MIGRATE CARDS ---
    if os.path.exists(CSV_FILES["cards"]):
        df = pd.read_csv(CSV_FILES["cards"])
        # Rename columns to match SQL schema defined above
        # Pandas to_sql is smart, but headers must match.
        # Let's force rename to be safe:
        df.columns = ["card_name", "closing_day", "due_day"]
        df.to_sql("cards", conn, if_exists="replace", index=False)
        print(f"✅ Migrated {len(df)} cards.")
    else:
        print("⚠️ No cards.csv found. Table 'cards' is empty.")


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        # 1. Connect
        conn = create_connection()

        # 2. Setup Structure
        create_tables(conn)

        # 3. Move Data
        migrate_csv_to_sql(conn)

        print(f"\n🚀 SUCCESS! Database '{DB_NAME}' is ready.")
        conn.close()

    except Exception as e:
        print(f"\n❌ Error: {e}")