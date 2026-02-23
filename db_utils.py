import sqlite3
import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta
from datetime import date as dt_class
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_NAME = "finance.db"


# --- 1. CORE DATA ENGINE ---

def get_connection():
    return sqlite3.connect(DB_NAME)


def run_query(query, params=()):
    """Standardized SQL Execution Engine."""
    with get_connection() as conn:
        if query.strip().upper().startswith("SELECT"):
            return pd.read_sql(query, conn, params=params)
        else:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return None


def load_data(table_name):
    """Standard loader with a safety net for missing tables."""
    try:
        res = run_query(f"SELECT * FROM {table_name}")
        return res if res is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def load_data_with_id(table_name):
    """ID-based loader."""
    return load_data(table_name)


# --- 2. OPERATIONAL LOGIC ---

def generate_installments(date, item, price, category, payment_method, installments):
    new_rows = []
    cards_df = load_data("cards")
    card_rule = cards_df[cards_df["card_name"] == payment_method]
    is_credit_card = not card_rule.empty

    for i in range(installments):
        if is_credit_card:
            closing_day = int(card_rule.iloc[0]["closing_day"])
            due_day = int(card_rule.iloc[0]["due_day"])
            months_to_add = i + (1 if date.day > closing_day else 0)
            row_date = (date + relativedelta(months=months_to_add)).replace(day=due_day)
        else:
            row_date = date + relativedelta(months=i)

        item_name = f"{item} ({i + 1}/{installments})" if installments > 1 else item
        new_rows.append(
            (row_date.strftime("%Y-%m-%d"), category, item_name, round(price / installments, 2), payment_method, 0))
    return new_rows


def check_and_insert_recurring():
    current_month_year = dt_class.today().strftime("%Y-%m")
    check_query = "SELECT COUNT(*) as cnt FROM expenses WHERE Item LIKE '%[AUTO]%' AND strftime('%Y-%m', Date) = ?"
    already_done_df = run_query(check_query, (current_month_year,))
    already_done = already_done_df.iloc[0, 0] if already_done_df is not None else 0

    if already_done == 0:
        recurring_items = run_query("SELECT * FROM recurring WHERE active = 1")
        if recurring_items is not None and not recurring_items.empty:
            for _, row in recurring_items.iterrows():
                day = min(int(row['day_of_month']), 28)
                target_date = dt_class.today().replace(day=day).strftime("%Y-%m-%d")
                new_item_name = f"{row['item']} [AUTO]"
                run_query("""
                          INSERT INTO expenses (Date, Category, Item, Price, "Payment Method", paid)
                          VALUES (?, ?, ?, ?, ?, ?)
                          """, (target_date, row['category'], new_item_name, row['price'], 'Pix', 0))
            return True
    return False


# --- 3. REPORTING & AUTOMATION ENGINE ---

def generate_monthly_summary_text():
    """Advanced Executive Summary with deep dive metrics."""
    today = pd.Timestamp.now()
    curr_month = today.strftime("%Y-%m")

    inc = load_data_with_id("incomes")
    exp = load_data_with_id("expenses")

    m_inc = inc[pd.to_datetime(inc['Date']).dt.strftime("%Y-%m") == curr_month] if not inc.empty else pd.DataFrame()
    m_exp = exp[pd.to_datetime(exp['Date']).dt.strftime("%Y-%m") == curr_month] if not exp.empty else pd.DataFrame()

    total_in = m_inc['Price'].sum() if not m_inc.empty else 0
    total_out = m_exp['Price'].sum() if not m_exp.empty else 0
    net = total_in - total_out
    savings_rate = (net / total_in * 100) if total_in > 0 else 0

    category_summary = ""
    if not m_exp.empty:
        cat_totals = m_exp.groupby("Category")["Price"].sum().sort_values(ascending=False)
        category_summary = "\n📊 TOP SPENDING CATEGORIES:\n"
        for cat, amt in cat_totals.items():
            category_summary += f"   - {cat}: R$ {amt:,.2f}\n"

    fiscal_status = "STABLE" if net >= 0 else "DEFICIT"
    mood_icon = "🟢" if net >= 0 else "🔴"

    return f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🛡️ LIFE OS 2026: FISCAL INTELLIGENCE REPORT
    📅 Period: {today.strftime('%B %Y')}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    💰 FINANCIAL OVERVIEW:
       • Gross Inflow:    R$ {total_in:,.2f}
       • Gross Outflow:   R$ {total_out:,.2f}
       • Net Cash Flow:   R$ {net:,.2f}
       • Savings Rate:    {savings_rate:.1f}%

    {category_summary}

    ⚖️ FISCAL HEALTH ASSESSMENT:
       Status: {mood_icon} {fiscal_status}
       {"Great job! You are living within your means." if net >= 0 else "Warning: Outflow exceeds inflow. Review your variable costs."}

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Sent via LifeOS Automated Dispatch | {today.strftime("%d/%m/%Y %H:%M")}
    """


def send_financial_report(recipient_email, subject, body):
    """Dispatches the report securely using Streamlit Secrets and SMTP."""
    try:
        sender_email = st.secrets["email"]["sender_email"]
        app_password = st.secrets["email"]["app_password"]
    except Exception:
        st.error("Credential Retrieval Failed: Check .streamlit/secrets.toml")
        return False

    if "your-email" in sender_email or "xxxx" in app_password:
        return False  # Silent return for auto-dispatch

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Mail Dispatch Failed: {e}")
        return False


def auto_dispatch_monthly_report(recipient_email):
    """
    Checks the log for current month. Sends report if missing.
    """
    # 1. Ensure log table exists
    run_query("CREATE TABLE IF NOT EXISTS report_logs (id INTEGER PRIMARY KEY, month_year TEXT UNIQUE, sent_at TEXT)")

    curr_month = pd.Timestamp.now().strftime("%Y-%m")

    # 2. Check the log
    check = run_query("SELECT * FROM report_logs WHERE month_year = ?", (curr_month,))

    if check is None or check.empty:
        report_body = generate_monthly_summary_text()
        success = send_financial_report(recipient_email, f"LifeOS Auto-Report: {curr_month}", report_body)

        if success:
            run_query("INSERT INTO report_logs (month_year, sent_at) VALUES (?, ?)",
                      (curr_month, pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")))
            return True
    return False