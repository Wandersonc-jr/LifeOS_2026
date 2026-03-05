import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from db_utils import generate_monthly_summary_text, send_financial_report
from dateutil.relativedelta import relativedelta
from datetime import date as dt_class


# --- 1. APP CONFIGURATION (Run once only) ---
st.set_page_config(
    page_title="LifeOS 2026 | Production",
    page_icon="🛡️",
    layout="wide"
)

# --- 2. SESSION STATE & NAVIGATION ---
if 'active_page' not in st.session_state:
    st.session_state.active_page = "📊 Dashboard"


def nav_to(page_name):
    st.session_state.active_page = page_name
    # No st.rerun here to prevent logic loops; the button click handles the refresh


# --- 3. DATABASE ENGINE ---
DB_NAME = "finance.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def run_query(query, params=()):
    with get_connection() as conn:
        if query.strip().upper().startswith("SELECT"):
            return pd.read_sql(query, conn, params=params)
        else:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return None


# --- 4. DATA LOADERS (Consolidated) ---
def load_full_system_data():
    df_exp = run_query("SELECT * FROM expenses")
    df_inc = run_query("SELECT * FROM incomes")
    df_inv = run_query("SELECT * FROM investments")
    df_bud = run_query("SELECT * FROM budgets")
    df_car = run_query("SELECT * FROM cards")

    # Standardize types immediately
    if df_exp is not None and not df_exp.empty:
        df_exp["Date"] = pd.to_datetime(df_exp["Date"])
    else:
        df_exp = pd.DataFrame(columns=["id", "Date", "Category", "Item", "Price", "Payment Method", "paid"])

    if df_inc is not None and not df_inc.empty:
        df_inc["Date"] = pd.to_datetime(df_inc["Date"])
    else:
        df_inc = pd.DataFrame(columns=["id", "Date", "Category", "Item", "Price"])

    return df_exp, df_inc, df_inv, df_bud, df_car


df_exp_all, df_inc_all, df_inv, df_budgets, df_cards = load_full_system_data()


# --- UI HELPER FUNCTIONS ---
def metric_card(label, value, color_bg, color_text, desc=""):
    """
    Standardized Fintech Metric Card.
    """
    st.markdown(f"""
    <div style="background: {color_bg}; padding: 18px; border-radius: 12px; border-left: 5px solid {color_text}; text-align: center; height: 120px; border-top: 1px solid rgba(255,255,255,0.05);">
        <p style="color: #8B949E; font-size: 11px; font-weight: bold; margin:0; text-transform: uppercase; letter-spacing: 0.5px;">{label}</p>
        <h2 style="margin:5px 0; border:none; font-size: 24px; color: white; font-weight: 800;">R$ {value:,.2f}</h2>
        <p style="margin:0; color: {color_text}; font-size: 11px; font-weight: bold; opacity: 0.9;">{desc}</p>
    </div>
    """, unsafe_allow_html=True)


# --- 3. SIDEBAR UI DESIGN ---
st.sidebar.title("🏦 LifeOS 2026")

st.sidebar.markdown("### 📈 STRATEGIC")
if st.sidebar.button("📊 Dashboard", use_container_width=True): nav_to("📊 Dashboard")
if st.sidebar.button("📈 Investments", use_container_width=True): nav_to("📈 Investments")
if st.sidebar.button("🎖️ Wealth Command", use_container_width=True): nav_to("🎖️ Wealth Command")

# TIER 2: GROWTH (New Sections)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 GROWTH")
if st.sidebar.button("🇺🇸 English Training", use_container_width=True): nav_to("English Training")
if st.sidebar.button("💻 Dev Portfolio", use_container_width=True): nav_to("Project Management")

st.sidebar.markdown("---")
st.sidebar.markdown("### 💸 OPERATIONAL")
if st.sidebar.button("💸 Expenses", use_container_width=True): nav_to("💸 Expenses")
if st.sidebar.button("💰 Incomes", use_container_width=True): nav_to("💰 Incomes")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ SYSTEM")
if st.sidebar.button("🎯 Set Budgets", use_container_width=True): nav_to("🎯 Set Budgets")
if st.sidebar.button("💳 Manage Cards", use_container_width=True): nav_to("💳 Manage Cards")
if st.sidebar.button("🔄 Recurring", use_container_width=True): nav_to("🔄 Recurring")
if st.sidebar.button("🏷️ Categories", use_container_width=True): nav_to("🏷️ Categories")

page = st.session_state.active_page
st.sidebar.info(f"📍 {page}")

# --- 4. DATA ENGINE & INFRASTRUCTURE PROVISIONING ---
DB_NAME = "finance.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def run_query(query, params=()):
    """
    Standardized SQL Execution Engine.
    Handles both Data Retrieval (SELECT) and State Changes (INSERT/UPDATE/DELETE).
    """
    with get_connection() as conn:
        if query.strip().upper().startswith("SELECT"):
            return pd.read_sql(query, conn, params=params)
        else:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return None


def initialize_system_db():
    """
    SECURITY & DATA INTEGRITY:
    Provision all required tables with standardized schemas.
    This ensures the 'Physical Infrastructure' of the database is sound.
    """
    # 1. CORE FINANCIALS
    run_query('''CREATE TABLE IF NOT EXISTS incomes
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     Date
                     TEXT,
                     Category
                     TEXT,
                     Item
                     TEXT,
                     Price
                     REAL
                 )''')

    run_query('''CREATE TABLE IF NOT EXISTS expenses
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     Date
                     TEXT,
                     Category
                     TEXT,
                     Item
                     TEXT,
                     Price
                     REAL,
                     "Payment Method"
                     TEXT,
                     paid
                     INTEGER
                     DEFAULT
                     0
                 )''')

    # 2. OPERATIONAL SETTINGS
    run_query("CREATE TABLE IF NOT EXISTS budgets (category TEXT PRIMARY KEY, amount REAL)")
    run_query("CREATE TABLE IF NOT EXISTS categories (name TEXT PRIMARY KEY, type TEXT)")
    run_query(
        "CREATE TABLE IF NOT EXISTS cards (id INTEGER PRIMARY KEY AUTOINCREMENT, card_name TEXT, closing_day INTEGER, due_day INTEGER, active INTEGER)")

    # 3. RECURRING & INVESTMENTS
    run_query('''CREATE TABLE IF NOT EXISTS recurring
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     item
                     TEXT,
                     category
                     TEXT,
                     price
                     REAL,
                     payment_method
                     TEXT,
                     day_of_month
                     INTEGER,
                     active
                     INTEGER
                     DEFAULT
                     1
                 )''')

    run_query('''CREATE TABLE IF NOT EXISTS investments
                 (
                     Asset
                     TEXT
                     PRIMARY
                     KEY,
                     Category
                     TEXT,
                     Date
                     TEXT,
                     Quantity
                     REAL,
                     Amount
                     REAL,
                     Current_Value
                     REAL
                 )''')

    # 4. GROWTH & PERFORMANCE (English & Projects)
    run_query('''CREATE TABLE IF NOT EXISTS vocabulary
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     word
                     TEXT,
                     sentence
                     TEXT,
                     date
                     TEXT
                 )''')

    run_query('''CREATE TABLE IF NOT EXISTS habit_list
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     habit_name
                     TEXT
                 )''')

    run_query('''CREATE TABLE IF NOT EXISTS daily_habits
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     habit_name
                     TEXT,
                     date
                     TEXT,
                     completed
                     INTEGER
                 )''')

    run_query('''CREATE TABLE IF NOT EXISTS dev_tasks
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     task_name
                     TEXT,
                     status
                     TEXT,
                     priority
                     TEXT,
                     completed
                     INTEGER
                 )''')


# --- TRIGGER BOOTSTRAP ---
# Must run before any data loaders are called
initialize_system_db()


# --- 5. FAULT-TOLERANT LOADERS ---
def load_data(table_name):
    """Fetches data but prevents crashes if the table hasn't been initialized yet."""
    try:
        res = run_query(f"SELECT * FROM {table_name}")
        return res if res is not None else pd.DataFrame()
    except Exception:
        # Graceful Degradation: Return empty DF to keep the UI running
        return pd.DataFrame()


def load_data_with_id(table_name):
    """Same as load_data, optimized for tables requiring physical IDs."""
    try:
        res = run_query(f"SELECT * FROM {table_name}")
        return res if res is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


# --- GLOBAL REFRESH ---
df_exp_all = load_data_with_id("expenses")
df_inc_all = load_data_with_id("incomes")
df_inv = load_data("investments")
df_budgets = load_data("budgets")
df_rec = load_data_with_id("recurring")
df_cats = load_data("categories")
if not df_cats.empty:
    df_cats = df_cats.sort_values("name", ascending=True)  # Forces A-Z globally

# Standardize Dates
if not df_exp_all.empty: df_exp_all["Date"] = pd.to_datetime(df_exp_all["Date"])
if not df_inc_all.empty: df_inc_all["Date"] = pd.to_datetime(df_inc_all["Date"])


# --- 5. LOGIC ENGINE ---
def generate_installments(date, item, price, category, payment_method, installments):
    new_rows = []
    cards_df = load_data("cards")
    card_rule = cards_df[cards_df["card_name"] == payment_method]
    is_credit_card = not card_rule.empty

    for i in range(installments):
        if is_credit_card:
            closing_day = int(card_rule.iloc[0]["closing_day"])
            due_day = int(card_rule.iloc[0]["due_day"])

            # 1. Base adjustment: If purchase is after closing, it belongs to next cycle (+1)
            cycle_shift = 1 if date.day > closing_day else 0

            # 2. Due month logic: If due_day < closing_day, bank gives you extra month to pay.
            due_month_offset = 1 if due_day < closing_day else 0

            months_to_add = i + cycle_shift + due_month_offset

            row_date = (date + relativedelta(months=months_to_add)).replace(day=due_day)
        else:
            row_date = date + relativedelta(months=i)

        item_name = f"{item} ({i + 1}/{installments})" if installments > 1 else item
        new_rows.append(
            (row_date.strftime("%Y-%m-%d"), category, item_name, round(price / installments, 2), payment_method, 0))
    return new_rows


# Global Data Refresh for UI
df_exp_all = load_data("expenses")
df_inc_all = load_data("incomes")
df_inv = load_data("investments")
df_budgets = load_data("budgets")

if not df_exp_all.empty: df_exp_all["Date"] = pd.to_datetime(df_exp_all["Date"])
if not df_inc_all.empty: df_inc_all["Date"] = pd.to_datetime(df_inc_all["Date"])



# ==============================================================================
# PAGE 1: DASHBOARD
# ==============================================================================
if page == "📊 Dashboard":

    # --- 1. DATA PREP (Unified Pipeline) ---
    today = pd.Timestamp.now()
    curr_month_str = today.strftime("%Y-%m")
    view_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Standardize dates for the whole session
    for df in [df_exp_all, df_inc_all]:
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"])
            # Ensure numeric 'paid' status (0 or 1)
            if 'paid' in df.columns:
                df["paid"] = pd.to_numeric(df["paid"], errors='coerce').fillna(0).astype(int)

    # --- 🟢 RECURRING LOGIC (Historical & Birth-Date Integrity) 🟢 ---
    df_rec_simulated = pd.DataFrame()
    if not df_rec.empty:
        df_rec['created_at'] = pd.to_datetime(df_rec['created_at'].fillna("2024-01-01"))
        mask_active_and_born = (df_rec['active'] == 1) & (df_rec['created_at'] <= view_month_start)
        active_rec_filtered = df_rec[mask_active_and_born].copy()

        if not active_rec_filtered.empty:
            df_rec_simulated = pd.DataFrame({
                'Item': active_rec_filtered['item'],
                'Category': active_rec_filtered['category'],
                'Price': active_rec_filtered['price'],
                'Date': [today.replace(day=1)] * len(active_rec_filtered),
                'paid': [0] * len(active_rec_filtered)
            })

    # --- 🔵 MONTHLY CALCULATIONS (The Operational Plan) 🔵 ---
    # Logged Incomes this month (March Target)
    m_inc = df_inc_all[
        df_inc_all["Date"].dt.strftime("%Y-%m") == curr_month_str] if not df_inc_all.empty else pd.DataFrame()
    income_val = m_inc["Price"].sum() if not m_inc.empty else 0.0

    # Logged Expenses this month (March Commitment)
    m_exp_raw = df_exp_all[df_exp_all["Date"].dt.strftime("%Y-%m") == curr_month_str].copy()
    m_exp = pd.concat([m_exp_raw, df_rec_simulated], ignore_index=True) if not df_rec_simulated.empty else m_exp_raw
    expense_val = m_exp["Price"].sum()

    # --- 🏛️ STRATEGIC TOTALS (The Actual Cash Reality) ---
    # Total Cash = ALL Received Incomes (Jan + Feb + Mar...) - ALL Paid Expenses
    total_received_all = df_inc_all[df_inc_all["paid"] == 1]["Price"].sum() if not df_inc_all.empty else 0.0
    total_paid_exp_all = df_exp_all[df_exp_all["paid"] == 1]["Price"].sum() if not df_exp_all.empty else 0.0

    # This is your real bank balance. It updates when you mark ANY row (January or March) as paid.
    total_cash = total_received_all - total_paid_exp_all

    # --- 📊 OPERATIONAL METRICS ---
    # Settled MTD: Only expenses dated this month that you have actually paid
    paid_mtd = m_exp_raw[m_exp_raw["paid"] == 1]["Price"].sum() if not m_exp_raw.empty else 0.0

    # DISPOSABLE: Your total cash currently in the bank
    # This reflects your REAL spending power at this exact second.
    disposable_income = total_cash

    # Burn Rate (Based on total commitments vs total expected income)
    burn_rate = (expense_val / income_val * 100) if income_val > 0 else 0.0

    total_invested = df_inv["Amount"].sum() if not df_inv.empty else 0.0
    net_worth = total_cash + total_invested

    # --- ZONE 1: STRATEGIC CAPITAL ---
    st.markdown("## 🏛️ Strategic Capital")
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Liquid Assets", total_cash, "rgba(59, 130, 246, 0.1)", "#3b82f6", "Real Bank Balance")
    with c2:
        metric_card("Invested Capital", total_invested, "rgba(139, 92, 246, 0.1)", "#8b5cf6", "Yield Assets")
    with c3:
        metric_card("Net Equity", net_worth, "rgba(16, 185, 129, 0.1)", "#10b981", "Total System Value")

    st.divider()

    # --- ZONE 2: OPERATIONAL VELOCITY ---
    st.markdown("### 📊 Operational Velocity")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        # Expected income for the current month only
        metric_card("Gross Inflow", income_val, "rgba(16, 185, 129, 0.05)", "#10b981",
                    f"Plan for {today.strftime('%b')}")
    with m2:
        metric_card("Gross Outflow", expense_val, "rgba(239, 68, 68, 0.05)", "#ef4444", f"Burn: {burn_rate:.1f}%")
    with m3:
        # Expenses dated this month that are settled
        metric_card("Cleared Debts", paid_mtd, "rgba(245, 158, 11, 0.05)", "#f59e0b", "Actually Paid (MTD)")
    with m4:
        # This now reacts to the January payment you marked!
        metric_card("Disposable", disposable_income, "rgba(59, 130, 246, 0.05)", "#3b82f6", "Cash-in-Hand")

    # --- ZONE 3: BUDGET VS ACTUAL ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎯 Budget Guardrails")
    if not df_budgets.empty:
        exp_by_cat = m_exp.groupby("Category")["Price"].sum().reset_index()
        comp_df = pd.merge(df_budgets, exp_by_cat, left_on="category", right_on="Category", how="left").fillna(0)
        comp_df["% Used"] = (comp_df["Price"] / comp_df["amount"] * 100).round(1)

        fig_budget = px.bar(comp_df, x="category", y=["amount", "Price"],
                            barmode="group",
                            labels={"value": "Amount (R$)", "variable": "Metric", "category": "Category"},
                            title="Spending vs. Monthly Limits",
                            color_discrete_map={"amount": "#3b82f6", "Price": "#ef4444"},
                            template="plotly_dark")
        st.plotly_chart(fig_budget, use_container_width=True)

        cols = st.columns(len(comp_df))
        for i, row in comp_df.iterrows():
            with cols[i]:
                color = "#10b981" if row["% Used"] < 80 else "#f59e0b" if row["% Used"] < 100 else "#ef4444"
                st.markdown(f"""
                    <div style="text-align: center; padding: 5px; border-top: 3px solid {color}; background: rgba(255,255,255,0.02); border-radius: 5px;">
                        <p style="margin:0; font-size: 0.7rem; color: #8B949E;">{row['category']}</p>
                        <p style="margin:0; font-size: 0.9rem; font-weight: bold; color: {color};">{row['% Used']}%</p>
                    </div>
                """, unsafe_allow_html=True)

    # --- ZONE 4: PENDING OBLIGATIONS ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💳 Liability & Settlement Pipeline")

    # 1. DEFINE PRECISES MONTHLY BOUNDARIES
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + relativedelta(months=1)) - relativedelta(seconds=1)

    if not df_exp_all.empty:
        # DATA PIPELINE: Force clean types for the filter
        df_pipe = df_exp_all.copy()
        df_pipe["Date"] = pd.to_datetime(df_pipe["Date"])

        # CRITICAL: Force 'paid' to numeric. 0 = Unpaid, 1 = Paid.
        # This ensures "Horti Frutti" and "Financing" items aren't skipped by mistake
        df_pipe["paid"] = pd.to_numeric(df_pipe["paid"], errors='coerce').fillna(0).astype(int)

        # FILTER: Unpaid AND strictly within this month
        mask_pending = (
                (df_pipe["paid"] == 0) &
                (df_pipe["Date"] >= start_of_month) &
                (df_pipe["Date"] <= end_of_month)
        )
        unpaid_current = df_pipe[mask_pending].copy()
    else:
        unpaid_current = pd.DataFrame()

    # 2. FILTER RECURRING
    active_recurring_settle = pd.DataFrame()
    if not df_rec.empty:
        active_recurring_settle = df_rec[
            (df_rec['active'] == 1) &
            (pd.to_datetime(df_rec['created_at'].fillna("2024-01-01")) <= start_of_month)
            ].copy()

    # 3. RENDER TABS
    if not unpaid_current.empty or not active_recurring_settle.empty:
        tab_cards, tab_tasks, tab_rec_pending = st.tabs([
            "💳 Institutional Debt (Cards)",
            "💸 Direct Settlements (Pix/Cash)",
            "🔄 Fixed Subscriptions"
        ])

        with tab_cards:
            # Filter for Credit Cards (Everything NOT Pix/Cash)
            cards_only = unpaid_current[~unpaid_current["Payment Method"].isin(["Pix", "Cash"])]

            if not cards_only.empty:
                card_sums = cards_only.groupby("Payment Method")["Price"].sum().reset_index()
                cols = st.columns(len(card_sums))

                for i, row in card_sums.iterrows():
                    bank_name = row['Payment Method']
                    with cols[i]:
                        st.markdown(f"""
                            <div style="background: rgba(255, 75, 75, 0.1); padding: 15px; border-radius: 10px; border: 1px solid rgba(255, 75, 75, 0.2); text-align: center;">
                                <p style="margin:0; font-size: 0.8rem; color: #94a3b8;">{bank_name}</p>
                                <h3 style="margin:0; color: #ff4b4b;">R$ {row['Price']:,.2f}</h3>
                            </div>
                        """, unsafe_allow_html=True)

                        # DETAILS LIST: Now you will see all 20+ items here
                        with st.expander(f"View {bank_name} items"):
                            details = cards_only[cards_only["Payment Method"] == bank_name]
                            st.dataframe(details[["Date", "Item", "Price"]], hide_index=True, use_container_width=True)

                        if st.button(f"Settle {bank_name} Month", key=f"btn_settle_{bank_name}",
                                     use_container_width=True):
                            target_ids = details["id"].tolist()
                            placeholders = ','.join(['?'] * len(target_ids))
                            run_query(f'UPDATE expenses SET paid = 1 WHERE id IN ({placeholders})', target_ids)
                            st.toast(f"{bank_name} balance cleared!")
                            st.rerun()
            else:
                st.success("No card installments due this month. ✅")

        with tab_tasks:
            pix_cash = unpaid_current[unpaid_current["Payment Method"].isin(["Pix", "Cash"])].copy()
            if not pix_cash.empty:
                edited_df = st.data_editor(
                    pix_cash[["id", "Date", "Category", "Item", "Price", "paid"]],
                    hide_index=True, use_container_width=True, key="editor_monthly_pix_final",
                    column_config={
                        "id": None,
                        "Date": st.column_config.DateColumn("Due Date", format="DD/MM/YYYY"),
                        "paid": st.column_config.CheckboxColumn("Settle?")
                    },
                    disabled=["Date", "Category", "Item", "Price"]
                )
                for i in range(len(edited_df)):
                    if edited_df.iloc[i]["paid"] == 1:
                        run_query("UPDATE expenses SET paid = 1 WHERE id = ?", (int(edited_df.iloc[i]["id"]),))
                        st.rerun()
            else:
                st.success("No manual payments pending for this month. ✅")

        with tab_rec_pending:
            if not active_recurring_settle.empty:
                st.caption(f"Subscriptions for {today.strftime('%B %Y')}:")
                current_month_names = m_exp_raw["Item"].tolist() if not m_exp_raw.empty else []
                pending_recurring = active_recurring_settle[~active_recurring_settle['item'].isin(current_month_names)]

                if not pending_recurring.empty:
                    for _, r_row in pending_recurring.iterrows():
                        c1, c2, c3 = st.columns([3, 1, 1])
                        c1.markdown(f"**{r_row['item']}**")
                        c2.markdown(f"R$ {r_row['price']:,.2f}")
                        if c3.button("Settle", key=f"log_rec_{r_row['id']}", use_container_width=True):
                            run_query(
                                'INSERT INTO expenses (Date, Category, Item, Price, "Payment Method", paid) VALUES (?, ?, ?, ?, ?, ?)',
                                (today.strftime("%Y-%m-%d"), r_row['category'], r_row['item'], r_row['price'],
                                 r_row['payment_method'], 1))
                            st.toast(f"Logged: {r_row['item']}")
                            st.rerun()
                else:
                    st.success("✨ All fixed subscriptions for this month settled.")

    # --- TIER 4: INTELLIGENCE HUB ---
    st.divider()
    st.markdown("### 🕵️‍♂️ Intelligence Hub")

    with st.expander("🔍 Deep Data Analysis & Prediction", expanded=False):
        date_selection = st.date_input(
            "Analysis Period",
            value=(today.date(), (today + relativedelta(months=1)).date()),
            key="intel_hub_v6_final"
        )

        # CRITICAL FIX: Ensure start and end exist before running
        if isinstance(date_selection, (list, tuple)) and len(date_selection) == 2:
            start, end = pd.to_datetime(date_selection[0]), pd.to_datetime(date_selection[1])

            p_exp = df_exp_all.copy() if not df_exp_all.empty else pd.DataFrame(columns=["Date", "Price", "Category", "Item", "Payment Method"])
            if not p_exp.empty:
                p_exp["Date"] = pd.to_datetime(p_exp["Date"])
                p_exp = p_exp[(p_exp["Date"] >= start) & (p_exp["Date"] <= end)]

            # Simulation of Recurring for Future/Range
            if not df_rec.empty:
                df_rec['created_at'] = pd.to_datetime(df_rec['created_at'].fillna("2024-01-01"))
                num_months = (end.year - start.year) * 12 + (end.month - start.month) + 1
                rec_rows = []
                for i in range(num_months):
                    sim_month_date = start + relativedelta(months=i)
                    if sim_month_date <= end:
                        active_and_born = df_rec[(df_rec['active'] == 1) & (df_rec['created_at'] <= sim_month_date)]
                        for _, r_item in active_and_born.iterrows():
                            rec_rows.append({'Date': sim_month_date, 'Category': r_item['category'], 'Item': f"🔄 {r_item['item']}", 'Price': r_item['price'], 'Payment Method': 'Recurring', 'paid': 0})
                if rec_rows:
                    p_exp = pd.concat([p_exp, pd.DataFrame(rec_rows)], ignore_index=True)

            p_inc = df_inc_all.copy() if not df_inc_all.empty else pd.DataFrame(columns=["Date", "Price"])
            if not p_inc.empty:
                p_inc["Date"] = pd.to_datetime(p_inc["Date"])
                p_inc = p_inc[(p_inc["Date"] >= start) & (p_inc["Date"] <= end)]

            pred_inc, pred_exp = p_inc["Price"].sum() if not p_inc.empty else 0.0, p_exp["Price"].sum() if not p_exp.empty else 0.0
            net_pred = pred_inc - pred_exp
            status_color = "#10b981" if net_pred > 0 else "#ef4444"

            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.02); padding: 20px; border-radius: 15px; border-left: 10px solid {status_color}; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <p style="color: #8B949E; margin:0; font-size: 0.8rem; letter-spacing: 1px;">STRATEGIC FORECAST (INCL. RECURRING)</p>
                            <h1 style="margin:0; color: white;">R$ {net_pred:,.2f}</h1>
                        </div>
                        <div style="text-align: right;">
                            <p style="margin:0; font-size: 1.2rem; color: {status_color}; font-weight: bold;">{'SURPLUS' if net_pred > 0 else 'DEFICIT'}</p>
                            <p style="margin:0; color: #8B949E; font-size: 0.8rem;">{start.strftime('%d %b')} — {end.strftime('%d %b')}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            col_left, col_right = st.columns([2, 1])
            with col_left:
                st.markdown("##### 📊 Cash Flow Momentum")
                combined_list = []
                if not p_exp.empty:
                    e = p_exp.groupby(p_exp["Date"].dt.to_period("M").astype(str))["Price"].sum().reset_index(name="Price")
                    e["Type"] = "Expense"; combined_list.append(e)
                if not p_inc.empty:
                    i = p_inc.groupby(p_inc["Date"].dt.to_period("M").astype(str))["Price"].sum().reset_index(name="Price")
                    i["Type"] = "Income"; combined_list.append(i)
                if combined_list:
                    fig_mom = px.bar(pd.concat(combined_list), x="Date", y="Price", color="Type", barmode="group", template="plotly_dark", height=250, color_discrete_map={"Income": "#10b981", "Expense": "#ef4444"})
                    st.plotly_chart(fig_mom, use_container_width=True)

            with col_right:
                st.markdown("##### 💳 Card Utilization")
                if not p_exp.empty:
                    card_data_source = p_exp[p_exp['Payment Method'] != 'Recurring']
                    if not card_data_source.empty:
                        card_data = card_data_source.groupby("Payment Method")["Price"].sum().reset_index().sort_values("Price")
                        st.plotly_chart(px.bar(card_data, y="Payment Method", x="Price", orientation='h', template="plotly_dark", height=250, color_discrete_sequence=["#8b5cf6"]), use_container_width=True)

            st.divider()
            col_pie, col_leaks = st.columns([1, 2])
            with col_pie:
                st.markdown("##### 🍕 Category Mix")
                if not p_exp.empty:
                    st.plotly_chart(px.pie(p_exp, values="Price", names="Category", hole=0.6, template="plotly_dark", height=280), use_container_width=True)

            with col_leaks:
                st.markdown("##### 🕵️‍♂️ Top Spending Items")
                if not p_exp.empty:
                    leaks = p_exp.sort_values("Price", ascending=False).head(5)
                    for _, row in leaks.iterrows():
                        st.markdown(f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; margin-bottom: 5px; background: rgba(255,255,255,0.02); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                                <div style="flex-grow: 1;"><p style="margin:0; font-weight: bold; color: white;">{row['Item']}</p><p style="margin:0; font-size: 0.75rem; color: #8B949E;">{row['Category']} • {row['Date'].strftime('%d/%m/%Y')}</p></div>
                                <div style="text-align: right;"><p style="margin:0; font-weight: bold; color: #ef4444;">R$ {row['Price']:,.2f}</p></div>
                            </div>
                        """, unsafe_allow_html=True)

            st.divider()
            col_runway, col_audit = st.columns([1, 1.5])
            with col_runway:
                st.markdown("##### ⛽ Cash Runway")
                liquid_inc = df_inc_all[df_inc_all['paid'] == 1]['Price'].sum() if ('paid' in df_inc_all.columns and not df_inc_all.empty) else 0.0
                total_liquid = liquid_inc - (df_exp_all["Price"].sum() if not df_exp_all.empty else 0)
                days_diff = (end - start).days + 1
                daily_burn = (pred_exp / days_diff) if pred_exp > 0 else 1
                runway_days = max(0, total_liquid / daily_burn)
                color_runway = "#10b981" if runway_days > 90 else "#f59e0b" if runway_days > 30 else "#ef4444"
                st.markdown(f"""<div style="background: rgba(255,255,255,0.02); padding: 15px; border-radius: 12px; text-align: center; border: 1px solid rgba(255,255,255,0.05);"><h2 style="margin:0; color: {color_runway};">{int(runway_days)} Days</h2><p style="margin:0; font-size: 0.8rem; color: #8B949E;">Survival Days</p></div>""", unsafe_allow_html=True)

            with col_audit:
                st.markdown("##### ✂️ Optimization Audit")
                waste_keywords = ['ifood', 'uber', 'netflix', 'amazon', 'steam', 'delivery', 'burger', 'pizza', 'hbo', 'disney']
                if not p_exp.empty:
                    waste_items = p_exp[(p_exp['Category'].isin(['Leisure', 'Entertainment', 'Dining Out'])) | (p_exp['Item'].fillna('').str.lower().str.contains('|'.join(waste_keywords)))].copy()
                    if not waste_items.empty:
                        for _, row in waste_items.sort_values("Price", ascending=False).head(5).iterrows():
                            st.markdown(f"""<div style="display: flex; justify-content: space-between; padding: 5px 10px; background: rgba(255,255,255,0.03); border-radius: 5px; margin-bottom: 3px; border-left: 4px solid #ef4444;"><span style="font-size: 0.85rem; color: #EEE; font-weight: bold;">{row['Item']}</span><span style="font-size: 0.85rem; font-weight: bold; color: #ef4444;">R$ {row['Price']:,.2f}</span></div>""", unsafe_allow_html=True)

            st.divider()
            st.markdown("##### 🎯 Savings Goal Progress")
            target_rate, current_rate = 0.30, (net_pred / pred_inc) if pred_inc > 0 else 0
            st.progress(min(1.0, max(0.0, current_rate / target_rate)))
            st.write(f"**{current_rate * 100:.1f}%** / {target_rate * 100:.0f}%")

    # --- TIER 5: NOTIFICATIONS ---
    st.divider()
    with st.expander("📧 Notification Center"):
        col_notif1, col_notif2 = st.columns([2, 1])
        user_email = col_notif1.text_input("Report Recipient", placeholder="your@email.com")
        if st.button("📧 Dispatch Monthly Report"):
            if user_email:
                report_body = generate_monthly_summary_text(df_inc_all, df_exp_all)
                if send_financial_report(user_email, "LifeOS Summary", report_body):
                    st.success("Report dispatched!")
# ==============================================================================
# PAGE: INVESTMENTS
# ==============================================================================
elif page == "📈 Investments":
    st.markdown("## 🏛️ Portfolio Strategy")
    st.markdown("<p style='color: #8B949E; margin-top: -15px;'>Strategic asset management and position tracking.</p>",
                unsafe_allow_html=True)

    # 1. INPUT & TRANSACTION FORM
    with st.expander("📝 Log Buy/Sell Transaction", expanded=True):
        with st.form("inv_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            asset_name = c1.text_input("Asset Ticker (e.g., ALRX11)").upper().strip()

            # Dynamic Categories
            df_cats_inv = load_data("categories")
            inv_cats = df_cats_inv[df_cats_inv['type'] == 'Investment']['name'].tolist()
            category = c2.selectbox("Category", inv_cats if inv_cats else ["Stocks", "FIIs", "Crypto"])
            purchase_date = c3.date_input("Transaction Date")

            c4, c5 = st.columns(2)
            quantity = c4.number_input("Quantity to Add", min_value=0.0, step=1.0,
                                       help="Amount purchased in this transaction")
            total_paid = c5.number_input("Total Price Paid", min_value=0.0, step=10.0,
                                         help="Total cost of this specific transaction")

            if st.form_submit_button("Log Transaction"):
                if asset_name and quantity > 0:
                    # THE ACCUMULATOR LOGIC:
                    # If ticker exists, ADD quantity and amount. If not, INSERT new.
                    run_query("""
                              INSERT INTO investments (Asset, Category, Date, Quantity, Amount, Current_Value)
                              VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(Asset) DO
                              UPDATE
                              SET
                                  Quantity = Quantity + excluded.Quantity, Amount = Amount + excluded.Amount, Date = excluded.Date, Category = excluded.Category
                              """, (asset_name, category, purchase_date, quantity, total_paid, total_paid))

                    st.success(f"Successfully added {quantity} units to {asset_name}!")
                    st.rerun()

    # 2. DATA LOAD
    df_inv = load_data("investments")

    if not df_inv.empty:
        # Avoid division by zero
        df_inv['Avg Price'] = df_inv['Amount'] / df_inv['Quantity'].replace(0, 1)

        # --- TOP METRICS ---
        total_invested = df_inv["Amount"].sum()
        m1, m2 = st.columns(2)
        with m1:
            st.metric("TOTAL CAPITAL ALLOCATED", f"R$ {total_invested:,.2f}")
        with m2:
            st.metric("TOTAL ASSETS", len(df_inv), delta="Active Positions")

        # --- VISUAL CHARTS ---
        st.divider()
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("#### 📁 Asset Allocation")
            fig_pie = px.pie(df_inv, values="Amount", names="Category", hole=0.5,
                             template="plotly_dark", color_discrete_sequence=px.colors.sequential.Blues_r)
            fig_pie.update_layout(margin=dict(t=20, b=20, l=0, r=0), showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_chart2:
            st.markdown("#### 📊 Portfolio Concentration")
            fig_bar = px.bar(df_inv, x="Asset", y="Amount", color="Category",
                             template="plotly_dark", text_auto='.2s')
            fig_bar.update_layout(margin=dict(t=20, b=20, l=0, r=0))
            st.plotly_chart(fig_bar, use_container_width=True)

        # --- 3. THE LEDGER (The Table) ---
        st.divider()
        st.markdown("### 📜 Portfolio Ledger")

        # Wrapped in a container for design
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.dataframe(
            df_inv[["Asset", "Category", "Quantity", "Avg Price", "Amount"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Asset": st.column_config.TextColumn("Ticker"),
                "Avg Price": st.column_config.NumberColumn("Avg. Cost", format="R$ %.2f"),
                "Amount": st.column_config.NumberColumn("Total Cost", format="R$ %.2f"),
                "Quantity": st.column_config.NumberColumn("Total Qty")
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 4. DELETE / LIQUIDATE
        with st.expander("🗑️ Close Position"):
            st.warning("This will permanently remove the asset record from your ledger.")
            target_del = st.selectbox("Select ticker to remove", df_inv["Asset"].tolist(), key="del_inv_selector")
            if st.button("Delete Asset Permanently"):
                run_query("DELETE FROM investments WHERE Asset = ?", (target_del,))
                st.success(f"Position {target_del} liquidated.")
                st.rerun()
# ==============================================================================
# PAGE 2: EXPENSES
# ==============================================================================
elif page == "💸 Expenses":
    st.markdown("## 💸 Expense Management")

    # 1. FETCH LATEST CATEGORIES (The Fix for Cybersecurity)
    df_cats_local = load_data("categories")
    if not df_cats_local.empty:
        # Filter by type and sort by name
        expense_cats = df_cats_local[df_cats_local['type'] == 'Expense'].sort_values("name")['name'].tolist()
    else:
        expense_cats = sorted(["Food", "Transport", "Housing", "Fun", "Investments"])  # Fallback

    # Fallback in case the category table is empty
    if not expense_cats:
        expense_cats = ["Food", "Transport", "Housing", "Fun", "Investments"]

    with st.expander("➕ New Transaction", expanded=True):
        with st.form("expense_form", clear_on_submit=True):
            r1c1, r1c2, r1c3 = st.columns([1, 2, 1])
            d, item, pr = r1c1.date_input("Date"), r1c2.text_input("Item"), r1c3.number_input("Price", step=0.01)

            r2c1, r2c2, r2c3 = st.columns(3)

            # USE THE DYNAMIC LIST HERE
            cat = r2c1.selectbox("Category", expense_cats)

            cards_df = load_data("cards")
            # Only show active cards
            card_list = (cards_df[cards_df['active'] == 1]['card_name'].tolist() if not cards_df.empty else [])
            meth = r2c2.selectbox("Method", ["Pix", "Cash"] + card_list)

            inst = r2c3.number_input("Installments", 1, 24, 1)

            if st.form_submit_button("Confirm Transaction"):
                # 1. Ensure 'd' is converted to a string format SQLite likes if it isn't already
                rows = generate_installments(d, item, pr, cat, meth, inst)

                # 2. Safety Check: Convert the first element of each tuple (the date) to string
                # Your current generate_installments might already do this, but let's be explicit:
                formatted_rows = [
                    (r[0].strftime("%Y-%m-%d") if not isinstance(r[0], str) else r[0],
                     r[1], r[2], r[3], r[4], r[5])
                    for r in rows
                ]

                conn = get_connection()
                conn.cursor().executemany(
                    'INSERT INTO expenses (Date, Category, Item, Price, "Payment Method", paid) VALUES (?, ?, ?, ?, ?, ?)',
                    formatted_rows)
                conn.commit()
                st.toast("Logged!", icon="✅")
                st.rerun()

    st.divider()
    st.markdown("### 📜 History & Maintenance")

    # --- 🟢 FILTER & SEARCH SECTION 🟢 ---
    c_search, c_filter = st.columns([2, 1])
    search_query = c_search.text_input("🔍 Search Item", placeholder="Search by name...", key="exp_search_box")

    cat_list = df_exp_all["Category"].unique().tolist() if not df_exp_all.empty else []
    selected_cats = c_filter.multiselect("📂 Filter Categories", options=cat_list, key="exp_filter_cats")

    # Load and Filter
    df_exp_display = load_data("expenses")

    if not df_exp_display.empty:
        # Pre-process for display
        df_exp_display["Date"] = pd.to_datetime(df_exp_display["Date"])

        # 1. Convert to boolean for filtering
        df_exp_display["paid"] = df_exp_display["paid"].astype(bool)

        # 🟢 FILTER: Hide everything already paid to focus on pending items
        df_exp_display = df_exp_display[df_exp_display["paid"] == False]

        # Apply Search and Category Filters
        if search_query:
            df_exp_display = df_exp_display[df_exp_display["Item"].str.contains(search_query, case=False, na=False)]
        if selected_cats:
            df_exp_display = df_exp_display[df_exp_display["Category"].isin(selected_cats)]

    if not df_exp_display.empty:
        cv, cd = st.columns([3, 1])
        with cv:
            st.dataframe(
                df_exp_display.sort_values("Date", ascending=False),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),  # 🟢 ID VISIBLE
                    "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                    "Price": st.column_config.NumberColumn("Price", format="R$ %.2f"),
                    "paid": st.column_config.CheckboxColumn("Paid?")
                }
            )
        with cd:
            st.markdown("🗑️ **Delete Record**")
            # Selector remains synced with the filtered view
            target_list = (df_exp_display["id"].astype(str) + " - " + df_exp_display["Item"]).tolist()
            target = st.selectbox("Select ID", target_list, key="del_exp_final")

            if st.button("Delete Permanently"):
                run_query("DELETE FROM expenses WHERE id = ?", (target.split(" - ")[0],))
                st.toast(f"Record {target.split(' - ')[0]} Removed")
                st.rerun()

        st.divider()
        with st.expander("✏️ Correct Expense History (Ledger Mode)"):
            st.info("Edit cells below to fix typos or wrong values. Changes save instantly.")
            # Ledger loads everything (even paid items) to allow full correction
            df_edit_exp = load_data("expenses")

            if not df_edit_exp.empty:
                # --- 🟢 DATA TYPE CONVERSION 🟢 ---
                # Standardize types to prevent StreamlitAPIException
                df_edit_exp["Date"] = pd.to_datetime(df_edit_exp["Date"])
                df_edit_exp["paid"] = df_edit_exp["paid"].astype(bool)

                edited_exp = st.data_editor(
                    df_edit_exp,
                    key="ledger_exp_page_v3",
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "id": st.column_config.NumberColumn("ID", width="small", disabled=True),
                        # 🟢 ID VISIBLE & PROTECTED
                        "paid": st.column_config.CheckboxColumn("Paid?"),
                        "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                        "Price": st.column_config.NumberColumn("Price", format="R$ %.2f")
                    }
                )

                # --- 🟢 UPDATE LOGIC 🟢 ---
                if not edited_exp.equals(df_edit_exp):
                    for i in range(len(edited_exp)):
                        if not edited_exp.iloc[i].equals(df_edit_exp.iloc[i]):
                            row = edited_exp.iloc[i]

                            # Convert Date object back to String for SQLite
                            db_date = row["Date"].strftime("%Y-%m-%d") if hasattr(row["Date"], "strftime") else row[
                                "Date"]

                            run_query("""UPDATE expenses
                                         SET Date=?,
                                             Category=?,
                                             Item=?,
                                             Price=?,
                                             "Payment Method"=?,
                                             paid=?
                                         WHERE id = ?""",
                                      (db_date, row["Category"], row["Item"], row["Price"],
                                       row["Payment Method"], int(row["paid"]), int(row["id"])))
                            st.toast(f"Updated ID {row['id']}: {row['Item']}")
                            st.rerun()

        st.divider()

# ==============================================================================
# PAGE 3: INCOMES
# ==============================================================================
elif page == "💰 Incomes":
    st.markdown("## 💰 Income Management")

    # --- 0. DATABASE INTEGRITY ---
    try:
        conn = get_connection()
        conn.cursor().execute("ALTER TABLE incomes ADD COLUMN paid INTEGER DEFAULT 1")
        conn.commit()
    except:
        pass

    # --- 1. DATA PREPARATION ---
    df_master_inc = load_data("incomes")
    today_dt = pd.Timestamp.now().normalize()
    curr_month_str = today_dt.strftime("%Y-%m")

    if not df_master_inc.empty:
        df_master_inc["Date"] = pd.to_datetime(df_master_inc["Date"])
        if "paid" not in df_master_inc.columns:
            df_master_inc["paid"] = 1
        else:
            df_master_inc["paid"] = pd.to_numeric(df_master_inc["paid"], errors='coerce').fillna(1)

        pending_all = df_master_inc[df_master_inc["paid"] == 0].copy()
        total_overdue = pending_all[pending_all["Date"] < today_dt]["Price"].sum()
        total_expected_mtd = pending_all[
            (pending_all["Date"] >= today_dt) &
            (pending_all["Date"].dt.strftime("%Y-%m") == curr_month_str)
            ]["Price"].sum()
        grand_total_pending = pending_all["Price"].sum()
        active_pending_list = pending_all.sort_values("Date")
    else:
        total_overdue, total_expected_mtd, grand_total_pending = 0.0, 0.0, 0.0
        active_pending_list = pd.DataFrame()

    # --- 2. RECEIVABLES RADAR ---
    st.markdown("### 📡 Receivables Radar")
    r1, r2, r3 = st.columns(3)
    with r1:
        metric_card("⚠️ Total Overdue", total_overdue, "rgba(239, 68, 68, 0.1)", "#ef4444", "Should be in bank")
    with r2:
        metric_card("📅 Month Forecast", total_expected_mtd, "rgba(245, 158, 11, 0.1)", "#f59e0b", "Coming soon")
    with r3:
        metric_card("💎 Total to Receive", grand_total_pending, "rgba(59, 130, 246, 0.1)", "#3b82f6",
                    "All Pending Assets")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. INPUT FORM ---
    df_cats_local = load_data("categories")
    income_cats = df_cats_local[df_cats_local['type'] == 'Income'].sort_values("name")[
        'name'].tolist() if not df_cats_local.empty else ["Salary"]

    with st.expander("➕ Log New Income Stream", expanded=False):
        with st.form("income_form", clear_on_submit=True):
            r1c1, r1c2, r1c3 = st.columns(3)
            d, cat, pr = r1c1.date_input("Date"), r1c2.selectbox("Category", income_cats), r1c3.number_input("Amount",
                                                                                                             step=0.01)
            item = st.text_input("Source/Description")
            received = st.checkbox("Received (Cash in hand?)", value=True)

            if st.form_submit_button("Confirm & Deposit"):
                try:
                    status = 1 if received else 0
                    run_query('INSERT INTO incomes (Date, Category, Item, Price, paid) VALUES (?, ?, ?, ?, ?)',
                              (d.strftime("%Y-%m-%d"), cat, item, pr, status))
                    st.toast("Inflow Recorded!", icon="💰")
                    st.rerun()
                except Exception as e:
                    st.error(f"Save Failed: {e}")

    st.divider()

    # --- 4. THE ACTION LIST (Awaiting Funds) ---
    st.markdown("### ⏳ Awaiting Funds")
    if not active_pending_list.empty:
        st.caption("Items disappear from here once checked, moving to your permanent history below.")

        # 🟢 Ensure types are correct for the editor
        active_pending_list["Date"] = pd.to_datetime(active_pending_list["Date"])
        active_pending_list["paid"] = active_pending_list["paid"].astype(bool)

        edited_pending = st.data_editor(
            active_pending_list[["id", "Date", "Category", "Item", "Price", "paid"]],
            hide_index=True, use_container_width=True, key="action_list_editor",
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),  # 🟢 ID VISIBLE
                "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                "paid": st.column_config.CheckboxColumn("Received?"),
                "Price": st.column_config.NumberColumn("Price", format="R$ %.2f")
            },
            disabled=["id", "Date", "Category", "Item", "Price"]  # 🟢 Only 'paid' is editable
        )

        for i in range(len(edited_pending)):
            if edited_pending.iloc[i]["paid"] == True:  # Check for boolean True
                run_query("UPDATE incomes SET paid = 1 WHERE id = ?", (int(edited_pending.iloc[i]["id"]),))
                st.toast(f"Income Received: {edited_pending.iloc[i]['Item']}")
                st.rerun()
    else:
        st.success("✨ All current receivables are cleared.")

    st.divider()

    # --- 🟢 5. NEW FILTER & SEARCH SECTION 🟢 ---
    st.markdown("### 🔍 Filter Historical Records")
    c_search, c_filter = st.columns([2, 1])
    search_inc = c_search.text_input("🔍 Search Income Source", placeholder="e.g., Salary, Client X...",
                                     key="inc_search_box")

    inc_cat_list = df_master_inc["Category"].unique().tolist() if not df_master_inc.empty else []
    selected_inc_cats = c_filter.multiselect("📂 Filter Categories", options=inc_cat_list, key="inc_filter_cats")

    # Applying the Filter to the Master List
    df_history_display = df_master_inc.copy()
    if not df_history_display.empty:
        # 🟢 Pre-process types for search and display
        df_history_display["Date"] = pd.to_datetime(df_history_display["Date"])
        df_history_display["paid"] = df_history_display["paid"].astype(bool)

        if search_inc:
            df_history_display = df_history_display[
                df_history_display["Item"].str.contains(search_inc, case=False, na=False)]
        if selected_inc_cats:
            df_history_display = df_history_display[df_history_display["Category"].isin(selected_inc_cats)]

    # --- 6. THE HISTORICAL LEDGER ---
    with st.expander("📜 Historical Ledger (Complete Archive)", expanded=True):
        st.info("Full record of all income. Toggle 'Rec.?' to revert status or use tools to delete.")
        if not df_history_display.empty:
            df_history_display = df_history_display.sort_values("Date", ascending=False)

            col_table, col_tools = st.columns([3, 1])
            with col_table:
                edited_history = st.data_editor(
                    df_history_display,
                    key="master_history_editor_v2",
                    hide_index=True, use_container_width=True,
                    column_config={
                        "id": st.column_config.NumberColumn("ID", width="small", disabled=True),
                        # 🟢 ID VISIBLE & LOCKED
                        "paid": st.column_config.CheckboxColumn("Rec.?"),
                        "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                        "Price": st.column_config.NumberColumn("Price", format="R$ %.2f")
                    }
                )

                if not edited_history.equals(df_history_display):
                    for i in range(len(edited_history)):
                        if not edited_history.iloc[i].equals(df_history_display.iloc[i]):
                            row = edited_history.iloc[i]

                            # Date standardization for SQL string format
                            date_str = row["Date"].strftime("%Y-%m-%d") if hasattr(row["Date"], "strftime") else str(
                                row["Date"])

                            run_query("""UPDATE incomes
                                         SET Date=?,
                                             Category=?,
                                             Item=?,
                                             Price=?,
                                             paid=?
                                         WHERE id = ?""",
                                      (date_str, row["Category"], row["Item"], row["Price"],
                                       int(row["paid"]), int(row["id"])))
                            st.toast(f"Updated Income ID {row['id']}")
                            st.rerun()
            with col_tools:
                st.markdown("🗑️ **Delete Record**")
                options = (df_history_display["id"].astype(str) + " - " + df_history_display["Item"]).tolist()
                target = st.selectbox("Select ID", options, key="del_final_inc")
                if st.button("Confirm Delete"):
                    run_query("DELETE FROM incomes WHERE id = ?", (target.split(" - ")[0],))
                    st.toast("Income Record Deleted")
                    st.rerun()
# ==============================================================================
# PAGE 5: SET BUDGETS
# ==============================================================================
elif page == "🎯 Set Budgets":
    st.markdown("## 🎯 Financial Guardrails")

    # Fetch latest to show current values in the input boxes
    latest_budgets = load_data("budgets")

    with st.form("budget_form"):
        # English Student Tip: Use "Thresholds" or "Allocations" for a native feel
        st.markdown("### Monthly Thresholds")

        # Get categories from your CATEGORIES table to stay synchronized
        # This prevents setting a budget for a category that doesn't exist
        cats = ["Food", "Transport", "Housing", "Fun", "Investments"]
        new_b = {}

        for c in cats:
            existing = latest_budgets[latest_budgets['category'] == c]['amount'].values
            new_b[c] = st.number_input(f"Monthly Limit: {c}",
                                       value=float(existing[0]) if len(existing) > 0 else 0.0,
                                       step=50.0)

        if st.form_submit_button("Update System Guardrails"):
            for c, a in new_b.items():
                run_query("INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)", (c, a))
            st.success("Guardrails updated successfully!")
            st.rerun()
# ==============================================================================
# PAGE: MANAGE CARDS
# ==============================================================================
elif page == "💳 Manage Cards":
    st.title("💳 Manage Cards")

    # THE FORM (Missing in previous snippet)
    with st.form("card_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Card Name (e.g. Nubank, Inter)")
        closing = c2.number_input("Closing Day", 1, 31, 1)
        due = c3.number_input("Due Day", 1, 31, 10)

        if st.form_submit_button("Save New Card"):
            if name:
                # We insert with active=1 by default
                run_query("INSERT INTO cards (card_name, closing_day, due_day, active) VALUES (?, ?, ?, 1)",
                          (name, int(closing), int(due)))
                st.success(f"Card {name} added!")
                st.rerun()

    st.divider()
    df_cards = load_data("cards")
    if not df_cards.empty:
        col_view, col_status = st.columns([3, 1])
        with col_view:
            st.dataframe(df_cards, use_container_width=True, hide_index=True)
        with col_status:
            st.markdown("⚙️ **Toggle Status**")
            options = (df_cards["id"].astype(str) + " - " + df_cards["card_name"]).tolist()
            target = st.selectbox("Select Card", options, key="status_card_ui")

            c1, c2 = st.columns(2)
            if c1.button("✅ Active"):
                run_query("UPDATE cards SET active = 1 WHERE id = ?", (target.split(" - ")[0],))
                st.rerun()
            if c2.button("❌ Inactive"):
                run_query("UPDATE cards SET active = 0 WHERE id = ?", (target.split(" - ")[0],))
                st.rerun()
# ==============================================================================
# PAGE: RECURRING
# ==============================================================================
elif page == "🔄 Recurring":
    st.markdown("## 🔄 Manage Fixed Expenses")

    # --- 0. INFRASTRUCTURE PATCH (Self-Healing) ---
    try:
        run_query("ALTER TABLE recurring ADD COLUMN created_at TEXT")
    except:
        pass  # Column already exists

    with st.form("recurring_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        item_name = c1.text_input("Service/Item (e.g. Netflix, Rent)")
        price = c2.number_input("Monthly Price", min_value=0.0, step=0.01)

        c3, c4 = st.columns(2)
        category = c3.selectbox("Category", ["Housing", "Son", "Fun", "Transport", "Food", "Education"])
        day = c4.number_input("Due Day of Month", 1, 31, 1)

        if st.form_submit_button("Add Subscription"):
            if item_name and price > 0:
                # Capture current month/year as the 'birth' of this subscription
                creation_date = pd.Timestamp.now().strftime("%Y-%m-01")
                run_query(
                    "INSERT INTO recurring (item, category, price, payment_method, day_of_month, active, created_at) VALUES (?, ?, ?, 'Pix', ?, 1, ?)",
                    (item_name, category, price, int(day), creation_date))
                st.success(f"Subscription for {item_name} active from {creation_date}!")
                st.rerun()

    st.divider()
    df_rec = load_data("recurring")
    if not df_rec.empty:
        # Fill empty created_at for old records so they don't break
        df_rec['created_at'] = df_rec['created_at'].fillna("2024-01-01")

        col_view, col_status = st.columns([3, 1.2])
        with col_view:
            st.dataframe(df_rec, use_container_width=True, hide_index=True)
        with col_status:
            st.markdown("⚙️ **Lifecycle Management**")
            options = (df_rec["id"].astype(str) + " - " + df_rec["item"]).tolist()
            target = st.selectbox("Select Service", options, key="status_rec_ui")
            target_id = target.split(" - ")[0]

            c1, c2 = st.columns(2)
            if c1.button("▶️ Resume"):
                run_query("UPDATE recurring SET active = 1 WHERE id = ?", (target_id,))
                st.rerun()
            if c2.button("⏸️ Pause"):
                run_query("UPDATE recurring SET active = 0 WHERE id = ?", (target_id,))
                st.rerun()

            st.markdown("---")
            if st.button("🗑️ Delete Permanently", use_container_width=True):
                run_query("DELETE FROM recurring WHERE id = ?", (target_id,))
                st.warning(f"Subscription removed from system.")
                st.rerun()
# ==============================================================================
# PAGE: CATEGORIES
# ==============================================================================
elif page == "🏷️ Categories":
    st.title("🏷️ Category Management")

    with st.form("cat_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        new_cat = c1.text_input("New Category Name")
        cat_type = c2.selectbox("Type", ["Expense", "Income", "Investment"])
        if st.form_submit_button("Add Category"):
            if new_cat:
                run_query("INSERT INTO categories (name, type) VALUES (?, ?)", (new_cat, cat_type))
                st.success(f"Category '{new_cat}' added!")
                st.rerun()

    st.divider()
    df_cats_display = load_data("categories")
    if not df_cats_display.empty:
        st.dataframe(df_cats_display, use_container_width=True, hide_index=True)

        # Delete Category
        target_cat = st.selectbox("Select Category to Delete", df_cats_display['name'].tolist())
        if st.button("Delete Category"):
            run_query("DELETE FROM categories WHERE name = ?", (target_cat,))
            st.rerun()

# ==============================================================================
# PAGE 4: WEALTH COMMAND (LONG-TERM STRATEGY)
# ==============================================================================
if page == "🎖️ Wealth Command":
    st.title("🎖️ Wealth Command & FIRE Strategy")
    st.markdown("### *Building your Financial Freedom*")

    # --- 1. DATA CALCULATIONS ---
    total_cash = (df_inc_all["Price"].sum() if not df_inc_all.empty else 0) - (
        df_exp_all["Price"].sum() if not df_exp_all.empty else 0)
    total_invested = df_inv["Amount"].sum() if not df_inv.empty else 0
    net_worth = total_cash + total_invested

    # Calculate Average Monthly Expense (Last 3 months or all time)
    if not df_exp_all.empty:
        # We look at the average cost of your lifestyle
        avg_monthly_exp = df_exp_all.groupby(df_exp_all["Date"].dt.to_period("M"))["Price"].sum().mean()
    else:
        avg_monthly_exp = 0.0

    # --- 2. THE FIRE CALCULATOR (Financial Independence, Retire Early) ---
    # Goal: Invested Assets = 25x Annual Expenses
    annual_expense_target = avg_monthly_exp * 12
    fire_number = annual_expense_target * 25

    progress_pct = min(total_invested / fire_number, 1.0) if fire_number > 0 else 0.0

    # Financial Runway (How many months can you survive without working?)
    runway_months = total_invested / avg_monthly_exp if avg_monthly_exp > 0 else 0

    st.divider()

    # --- 3. TOP LEVEL METRICS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Financial Runway", f"{runway_months:.1f} Months",
              help="How long your investments alone cover your lifestyle.")
    c2.metric("Annual Lifestyle Cost", f"R$ {annual_expense_target:,.2f}")
    c3.metric("FIRE Number", f"R$ {fire_number:,.2f}", help="25x your annual expenses.")

    # --- 4. VISUAL PROGRESS TO FREEDOM ---
    st.markdown(f"#### 🎯 Progress to Financial Independence: {progress_pct * 100:.1f}%")
    st.progress(progress_pct)

    if progress_pct < 1.0:
        remaining = fire_number - total_invested
        st.info(f"🚀 You are **R$ {remaining:,.2f}** away from your freedom goal.")
    else:
        st.balloons()
        st.success("🎊 You have reached Financial Independence!")

    st.divider()

    # --- 5. ASSET ALLOCATION (Visualizing where your wealth is) ---
    st.subheader("🏦 Asset Allocation")
    col_asset1, col_asset2 = st.columns([2, 1])

    with col_asset1:
        # Net Worth Trend (Simplified - Assets vs Cash)
        allocation_data = pd.DataFrame({
            "Source": ["Liquid Cash", "Invested Assets"],
            "Value": [total_cash, total_invested]
        })
        st.plotly_chart(px.pie(allocation_data, values="Value", names="Source",
                               hole=0.5, color_discrete_sequence=["#3b82f6", "#8b5cf6"],
                               template="plotly_dark"), use_container_width=True)

    with col_asset2:
        # Breakdown of Investments
        if not df_inv.empty:
            st.markdown("##### Investment Mix")
            inv_mix = df_inv.groupby("Category")["Amount"].sum().reset_index()
            st.plotly_chart(px.bar(inv_mix, x="Category", y="Amount", template="plotly_dark"), use_container_width=True)

    # --- 6. FREEDOM MILESTONES ---
    st.divider()
    st.subheader("🚩 Freedom Milestones")


    def milestone_box(label, amount, current):
        status = "✅" if current >= amount else "⏳"
        color = "#10b981" if current >= amount else "#94a3b8"
        st.markdown(f"""
            <div style="padding:10px; border-radius:10px; border-left: 5px solid {color}; background-color: #1a1c24; margin-bottom:10px;">
                <span style="color: {color}; font-weight: bold;">{status} {label}</span><br>
                <small style="color: #64748b;">Target: R$ {amount:,.2f}</small>
            </div>
        """, unsafe_allow_html=True)


    m1, m2, m3 = st.columns(3)
    with m1:
        milestone_box("Starter Emergency Fund", 1000, net_worth)
        milestone_box("3-Month Safety Net", avg_monthly_exp * 3, net_worth)
    with m2:
        milestone_box("1-Year Runway", avg_monthly_exp * 12, total_invested)
        milestone_box("Lean FIRE (Halfway)", fire_number / 2, total_invested)
    with m3:
        milestone_box("Coast FIRE", fire_number * 0.75, total_invested)
        milestone_box("FULL FREEDOM", fire_number, total_invested)

# ==============================================================================
# PAGE: ENGLISH TRAINING
# ==============================================================================
elif page == "English Training":
    # 1. DATABASE & SCHEMA SELF-HEALING (Consolidated Infrastructure)
    run_query('''CREATE TABLE IF NOT EXISTS vocabulary
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     word
                     TEXT,
                     sentence
                     TEXT,
                     date
                     TEXT
                 )''')
    run_query('''CREATE TABLE IF NOT EXISTS habit_list
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     habit_name
                     TEXT
                 )''')
    run_query('''CREATE TABLE IF NOT EXISTS daily_habits
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     habit_name
                     TEXT,
                     date
                     TEXT,
                     completed
                     INTEGER
                 )''')

    # Security Patch: Ensure Context Column exists
    try:
        run_query("SELECT sentence FROM vocabulary LIMIT 1")
    except:
        run_query("ALTER TABLE vocabulary ADD COLUMN sentence TEXT")
        st.rerun()

    st.markdown("<h1>🇺🇸 English Proficiency Hub</h1>", unsafe_allow_html=True)
    today_date = pd.Timestamp.now().strftime("%Y-%m-%d")

    col_rituals, col_vocab = st.columns([1, 1.3])

    # --- LEFT: DAILY RITUALS (Consistency Engine) ---
    with col_rituals:
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.markdown("### ✍️ Daily Rituals")

        # Fetch Master List and Today's Progress
        res_master = run_query("SELECT id, habit_name FROM habit_list")
        master_habits = res_master if res_master is not None and not res_master.empty else pd.DataFrame()

        res_done = run_query("SELECT habit_name FROM daily_habits WHERE date = ?", (today_date,))
        done_today = res_done["habit_name"].tolist() if res_done is not None and not res_done.empty else []

        if not master_habits.empty:
            for _, h_row in master_habits.iterrows():
                h_name = h_row['habit_name']
                h_id = h_row['id']
                is_done = h_name in done_today

                # Layout for Ritual Row
                r_col1, r_col2 = st.columns([5, 1])

                # Checkbox for Completion
                if r_col1.checkbox(h_name, value=is_done, key=f"rit_{h_id}_{today_date}"):
                    if not is_done:
                        run_query("INSERT INTO daily_habits (habit_name, date, completed) VALUES (?, ?, 1)",
                                  (h_name, today_date))
                        st.rerun()
                elif is_done:
                    run_query("DELETE FROM daily_habits WHERE habit_name = ? AND date = ?", (h_name, today_date))
                    st.rerun()
        else:
            st.info("No rituals defined. Provision your training plan below.")

        st.markdown("---")

        # --- THE MANAGEMENT ZONE (Fixes the delete issue) ---
        with st.expander("⚙️ System Housekeeping (Manage Rituals)"):
            # ADD NEW
            new_h = st.text_input("New Ritual Name", placeholder="e.g. Read 5 pages")
            if st.button("Add to Master List", use_container_width=True):
                if new_h:
                    run_query("INSERT INTO habit_list (habit_name) VALUES (?)", (new_h.strip(),))
                    st.rerun()

            st.divider()

            # DELETE EXISTING
            if not master_habits.empty:
                st.caption("⚠️ Destructive Action: Remove Habit Forever")
                target_to_del = st.selectbox("Select Habit to Purge", master_habits['habit_name'].tolist())
                if st.button("🗑️ Purge Habit from System", use_container_width=True):
                    # Delete from Master List
                    run_query("DELETE FROM habit_list WHERE habit_name = ?", (target_to_del,))
                    # Also delete historical logs to keep DB clean (Referential Integrity)
                    run_query("DELETE FROM daily_habits WHERE habit_name = ?", (target_to_del,))
                    st.warning(f"Habit '{target_to_del}' has been decommissioned.")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- RIGHT: EXPRESSION CAPTURE (The Lexicon) ---
    with col_vocab:
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.markdown("### 📓 Expression Capture")

        with st.container():
            c1, c2 = st.columns([1, 2])
            word_input = c1.text_input("New Term", key="vocab_term", placeholder="Slang / Idiom")
            sent_input = c2.text_input("Usage Context", key="vocab_sent", placeholder="Usage context...")

            if st.button("💾 Commit to Memory", use_container_width=True):
                if word_input:
                    run_query("INSERT INTO vocabulary (word, sentence, date) VALUES (?, ?, ?)",
                              (word_input.strip(), sent_input.strip(), today_date))
                    st.toast(f"Logged: {word_input}")
                    st.rerun()

        st.markdown("---")

        # Display acquisitions
        df_vocab = run_query("SELECT id, word, sentence FROM vocabulary ORDER BY id DESC LIMIT 6")

        if df_vocab is not None and not df_vocab.empty:
            st.markdown("#### 📜 Recent Acquisitions")
            for _, row in df_vocab.iterrows():
                context = row['sentence'] if row['sentence'] else "No context recorded."
                st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #58a6ff;">
                        <strong style="color: #58a6ff;">{row['word']}</strong><br>
                        <small style="color: #8B949E; font-style: italic;">{context}</small>
                    </div>
                """, unsafe_allow_html=True)

            # --- NEW DELETE LOGIC FOR VOCAB ---
            with st.expander("🗑️ Delete Expressions"):
                vocab_options = (df_vocab["id"].astype(str) + " - " + df_vocab["word"]).tolist()
                to_delete = st.selectbox("Select term to purge", vocab_options)
                if st.button("Purge from Lexicon"):
                    run_query("DELETE FROM vocabulary WHERE id = ?", (to_delete.split(" - ")[0],))
                    st.success("Word removed.")
                    st.rerun()
        else:
            st.caption("The lexicon is currently empty.")
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PAGE: PROJECT MANAGEMENT
# ==============================================================================
elif page == "Project Management":
    # 1. DATABASE & SCHEMA SELF-HEALING (Infrastructure Provisioning)
    run_query('''CREATE TABLE IF NOT EXISTS dev_tasks
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     task_name
                     TEXT,
                     status
                     TEXT,
                     priority
                     TEXT,
                     completed
                     INTEGER
                 )''')

    # Security Provisioning: Verify Priority Column
    try:
        run_query("SELECT priority FROM dev_tasks LIMIT 1")
    except:
        run_query("ALTER TABLE dev_tasks ADD COLUMN priority TEXT DEFAULT 'Medium'")
        st.rerun()

    st.markdown("<h1>💻 Security & Dev Portfolio</h1>", unsafe_allow_html=True)

    # 2. DATA INGESTION
    res = run_query("SELECT * FROM dev_tasks")
    df_tasks = res if res is not None and not res.empty else pd.DataFrame(
        columns=['id', 'task_name', 'status', 'priority', 'completed'])

    # 3. OPERATIONAL METRICS (Health Monitoring)
    sprint_tasks = df_tasks[df_tasks['status'] == 'Sprint'].copy()
    progress = sprint_tasks['completed'].mean() if not sprint_tasks.empty else 0

    st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
    st.markdown(f"### 🛡️ Remediation Velocity ({progress:.0%})")
    # Custom colored progress bar based on completion
    st.progress(progress)
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. LIFECYCLE TABS
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Active Sprint", "📂 Triage Queue", "🛠️ Provisioning", "📜 Audit Trail"])

    with tab1:
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.markdown("### 🏃 Execution Phase")

        if not sprint_tasks.empty:
            for _, row in sprint_tasks.iterrows():
                # Severity-based visual markers
                p_map = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                icon = p_map.get(row['priority'], "⚪")

                is_checked = bool(row['completed'])
                if st.checkbox(f"{icon} {row['task_name']}", value=is_checked, key=f"sprint_{row['id']}"):
                    if not is_checked:
                        run_query("UPDATE dev_tasks SET completed = 1 WHERE id = ?", (row['id'],))
                        st.rerun()
                elif is_checked:
                    run_query("UPDATE dev_tasks SET completed = 0 WHERE id = ?", (row['id'],))
                    st.rerun()

            st.divider()

            # INTEGRATED CLOSEOUT (Operation Cleanup)
            st.markdown("### 🧹 Quick Closeout")
            c_sel, c_arch, c_del = st.columns([2, 1, 1])

            target_list = sprint_tasks['task_name'].tolist()
            if target_list:
                target_name = c_sel.selectbox("Select Task to Finalize:", target_list, key="q_close")
                target_id = sprint_tasks[sprint_tasks['task_name'] == target_name]['id'].values[0]

                if c_arch.button("✅ Archive", use_container_width=True):
                    run_query("UPDATE dev_tasks SET status = 'Archived', completed = 1 WHERE id = ?", (int(target_id),))
                    st.toast(f"Requirement {target_id} moved to history.")
                    st.rerun()

                if c_del.button("🗑️ Purge", use_container_width=True):
                    run_query("DELETE FROM dev_tasks WHERE id = ?", (int(target_id),))
                    st.warning(f"Record {target_id} purged from system.")
                    st.rerun()
        else:
            st.info("No active tickets in the current sprint. Pipeline idle.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Risk Triage (Backlog)")
        backlog_items = df_tasks[df_tasks['status'] == 'Backlog'].copy()

        if not backlog_items.empty:
            for _, row in backlog_items.iterrows():
                col_item, col_btn = st.columns([3, 1])
                color = "🔴" if row['priority'] == "High" else "⚪"
                col_item.markdown(f"{color} **{row['task_name']}**")

                if col_btn.button("Promote to Sprint", key=f"prom_{row['id']}", use_container_width=True):
                    run_query("UPDATE dev_tasks SET status = 'Sprint' WHERE id = ?", (row['id'],))
                    st.rerun()
        else:
            st.success("Triage complete. No pending risks found.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.markdown("### 🛠️ Provision New Requirement")
        with st.form("new_req_form", clear_on_submit=True):
            col_a, col_b = st.columns([2, 1])
            name = col_a.text_input("Operational Requirement", placeholder="e.g., Audit firewall logs")
            priority = col_b.selectbox("Severity Level", ["Low", "Medium", "High"], index=1)
            stage = st.selectbox("Deployment Pipeline", ["Backlog", "Sprint"])

            if st.form_submit_button("Deploy to System"):
                if name:
                    run_query("INSERT INTO dev_tasks (task_name, status, priority, completed) VALUES (?, ?, ?, 0)",
                              (name.strip(), stage, priority))
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.markdown("### 📜 Historical Audit Trail")
        archived_tasks = df_tasks[df_tasks['status'] == 'Archived'].copy()

        if not archived_tasks.empty:
            st.dataframe(archived_tasks[['task_name', 'priority', 'completed']],
                         column_config={
                             "task_name": "Resolved Task",
                             "priority": "Severity",
                             "completed": st.column_config.CheckboxColumn("Validated")
                         },
                         hide_index=True, use_container_width=True)

            if st.button("Purge Audit History", help="Destructive action: removes all archived records"):
                run_query("DELETE FROM dev_tasks WHERE status = 'Archived'")
                st.rerun()
        else:
            st.caption("Audit trail empty. No historical data.")
        st.markdown('</div>', unsafe_allow_html=True)




# --- SYSTEM AUDIT TOOL ---
with st.sidebar.expander("🛡️ System Integrity Audit"):
    tables = ["expenses", "incomes", "budgets", "vocabulary", "dev_tasks"]
    for t in tables:
        try:
            count = run_query(f"SELECT COUNT(*) as cnt FROM {t}")
            st.write(f"✅ Table '{t}': {count['cnt'][0]} records found.")
        except Exception as e:
            st.error(f"❌ Table '{t}' is corrupted or missing columns: {e}")