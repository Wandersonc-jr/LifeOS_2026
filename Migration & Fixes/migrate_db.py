import sqlite3

def migrate_to_status():
    conn = sqlite3.connect("../finance.db")
    cursor = conn.cursor()

    # Add 'active' column to Recurring
    print("Updating Recurring table...")
    try:
        cursor.execute("ALTER TABLE recurring ADD COLUMN active INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        print("Column 'active' already exists in recurring.")

    # Add 'active' column to Cards
    print("Updating Cards table...")
    try:
        cursor.execute("ALTER TABLE cards ADD COLUMN active INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        print("Column 'active' already exists in cards.")

    conn.commit()
    conn.close()
    print("Migration Complete! You can now toggle status.")

if __name__ == "__main__":
    migrate_to_status()