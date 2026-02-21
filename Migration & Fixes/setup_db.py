import sqlite3
import pandas as pd

def get_connection():
    return sqlite3.connect("../finance.db")

def run_query(query, params=()):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

def load_data(table_name):
    with get_connection() as conn:
        try:
            return pd.read_sql(f"SELECT * FROM {table_name}", conn)
        except:
            return pd.DataFrame()