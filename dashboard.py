import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from dateutil.relativedelta import relativedelta
from datetime import date as dt_class

# --- TRIGGER AUTO-DISPATCH ---
try:
    user_email = st.secrets["email"]["sender_email"]
    if auto_dispatch_monthly_report(user_email):
        st.toast(f"📬 Monthly report sent automatically!", icon="🚀")
except Exception:
    pass # Secrets not configured yet

# Import our custom logic
import db_utils
from db_utils import * # --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="LifeOS 2026 | Production",
    page_icon="🛡️",
    layout="wide"
)

if 'active_page' not in st.session_state:
    st.session_state.active_page = "📊 Dashboard"

def nav_to(page_name):
    st.session_state.active_page = page_name
    st.rerun()

# --- UI HELPER FUNCTIONS ---
# --- UPDATE THIS FUNCTION ---
def metric_card(label, value, color_bg, color_text, desc=""):
    """
    Standardized Fintech Metric Card.
    Arguments:
    - label: The title of the metric
    - value: The numerical amount
    - color_bg: Background color (rgba)
    - color_text: Primary accent color (hex)
    - desc: Sub-text description
    """
    st.markdown(f"""
    <div style="background: {color_bg}; padding: 18px; border-radius: 12px; border-left: 5px solid {color_text}; text-align: center; height: 120px; border-top: 1px solid rgba(255,255,255,0.05);">
        <p style="color: #8B949E; font-size: 11px; font-weight: bold; margin:0; text-transform: uppercase; letter-spacing: 0.5px;">{label}</p>
        <h2 style="margin:5px 0; border:none; font-size: 24px; color: white; font-weight: 800;">R$ {value:,.2f}</h2>
        <p style="margin:0; color: {color_text}; font-size: 11px; font-weight: bold; opacity: 0.9;">{desc}</p>
    </div>
    """, unsafe_allow_html=True)

# --- 1. CONFIGURATION & PREMIUM UI ---
st.set_page_config(page_title="My Financial Core (SQL)", page_icon="🏦", layout="wide")

# Force uniform button and metric styling
st.markdown("""
    <style>
    .stButton > button { width: 100%; border-radius: 8px; height: 3rem; font-weight: 600; }
    [data-testid="stMetric"] { background-color: #1a1c24; padding: 20px; border-radius: 15px; border: 1px solid #30363d; transition: all 0.3s ease; }
    [data-testid="stMetric"]:hover { border-color: #58a6ff; transform: translateY(-2px); }
    .stProgress > div > div > div > div { background-color: #58a6ff; }
    </style>
""", unsafe_allow_html=True)

# --- 2. UX NAVIGATION CONTROLLER ---
if "active_page" not in st.session_state:
    st.session_state.active_page = "📊 Dashboard"


def nav_to(page_name):
    st.session_state.active_page = page_name


# --- 3. SIDEBAR UI DESIGN ---
st.sidebar.title("🏦 LifeOS 2026")

st.sidebar.markdown("### 📈 STRATEGIC")
if st.sidebar.button("📊 Dashboard", use_container_width=True): nav_to("📊 Dashboard")
if st.sidebar.button("📈 Investments", use_container_width=True): nav_to("📈 Investments")
if st.sidebar.button("📈 Wealth Command", use_container_width=True): nav_to("📈 Wealth Command")

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

# --- LOADERS ---
def load_data(table_name):
    """Standard loader for configuration tables."""
    res = run_query(f"SELECT * FROM {table_name}")
    return res if res is not None else pd.DataFrame()

def load_data_with_id(table_name):
    """
    Security Note: Since we use PRIMARY KEY AUTOINCREMENT on 'id',
    we no longer need to rely on the 'rowid' hack.
    """
    res = run_query(f"SELECT * FROM {table_name}")
    return res if res is not None else pd.DataFrame()

# --- GLOBAL REFRESH ---
df_exp_all = load_data_with_id("expenses")
df_inc_all = load_data_with_id("incomes")
df_inv = load_data("investments")
df_budgets = load_data("budgets")
df_rec = load_data_with_id("recurring")
df_cats = load_data("categories") # <--- Load categories here

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
            months_to_add = i + (1 if date.day > closing_day else 0)
            row_date = (date + relativedelta(months=months_to_add)).replace(day=due_day)
        else:
            row_date = date + relativedelta(months=i)
        item_name = f"{item} ({i + 1}/{installments})" if installments > 1 else item
        new_rows.append((row_date, category, item_name, round(price / installments, 2), payment_method, 0))
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

    # Standardize dates for the whole session
    for df in [df_exp_all, df_inc_all]:
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"])

    # Current Month Calculations
    m_exp = df_exp_all[
        df_exp_all["Date"].dt.strftime("%Y-%m") == curr_month_str] if not df_exp_all.empty else pd.DataFrame()
    m_inc = df_inc_all[
        df_inc_all["Date"].dt.strftime("%Y-%m") == curr_month_str] if not df_inc_all.empty else pd.DataFrame()

    income_val = m_inc["Price"].sum() if not m_inc.empty else 0.0
    expense_val = m_exp["Price"].sum() if not m_exp.empty else 0.0
    paid_mtd = m_exp[m_exp["paid"].isin([1, True, "1"])]["Price"].sum() if not m_exp.empty else 0.0

    # Terminology Refinement
    disposable_income = income_val - paid_mtd
    burn_rate = (expense_val / income_val * 100) if income_val > 0 else 0.0

    # Strategic Totals
    total_inc_all = df_inc_all["Price"].sum() if not df_inc_all.empty else 0.0
    total_exp_all = df_exp_all["Price"].sum() if not df_exp_all.empty else 0.0
    total_cash = total_inc_all - total_exp_all
    total_invested = df_inv["Amount"].sum() if not df_inv.empty else 0.0
    net_worth = total_cash + total_invested

    # --- ZONE 1: STRATEGIC CAPITAL (The "Block" Build) ---
    st.markdown("## 🏛️ Strategic Capital")
    c1, c2, c3 = st.columns(3)

    with c1:
        # Security Perspective: "Account Liquidity" - Immediate cash available for deployment
        metric_card("Liquid Assets", total_cash, "rgba(59, 130, 246, 0.1)", "#3b82f6", "Account Liquidity")
    with c2:
        # Native English: "Yield Assets" - Capital specifically allocated to grow
        metric_card("Invested Capital", total_invested, "rgba(139, 92, 246, 0.1)", "#8b5cf6", "Yield Assets")
    with c3:
        # Executive English: "Total System Value" - The ultimate health check
        metric_card("Net Equity", net_worth, "rgba(16, 185, 129, 0.1)", "#10b981", "Total System Value")

    st.divider()

    # --- ZONE 2: OPERATIONAL VELOCITY ---
    st.markdown("### 📊 Operational Velocity")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Gross Inflow", income_val, "rgba(16, 185, 129, 0.05)", "#10b981", "Total Revenue")
    with m2:
        metric_card("Gross Outflow", expense_val, "rgba(239, 68, 68, 0.05)", "#ef4444", f"Burn: {burn_rate:.1f}%")
    with m3:
        metric_card("Cleared Debts", paid_mtd, "rgba(245, 158, 11, 0.05)", "#f59e0b", "Settled MTD")
    with m4:
        metric_card("Disposable", disposable_income, "rgba(59, 130, 246, 0.05)", "#3b82f6", "Unallocated")

    # --- ZONE 3: PENDING OBLIGATIONS (The "Security" View) ---
    st.markdown("<br>", unsafe_allow_html=True)  # Requested blank space
    st.markdown("### 💳 Liability & Settlement Pipeline")

    # 1. Filtering Logic (Optimized for performance)
    today_cutoff = today.strftime("%Y-%m")
    if not df_exp_all.empty:
        mask_pending = (df_exp_all["paid"].isin([0, False, "0"]) &
                        (df_exp_all["Date"].dt.strftime("%Y-%m") <= today_cutoff))
        unpaid_current = df_exp_all[mask_pending].copy()
    else:
        unpaid_current = pd.DataFrame()

    # 2. UI Rendering
    if not unpaid_current.empty:
        # --- SECURITY RISK ASSESSMENT ---
        overdue = unpaid_current[unpaid_current["Date"].dt.strftime("%Y-%m") < today_cutoff]

        if not overdue.empty:
            # Using a native financial term: "Delinquent Accounts"
            st.error(
                f"🚨 **Critical Alert:** Found {len(overdue)} delinquent items from previous cycles. Immediate action required.")
        else:
            st.info("ℹ️ **Status:** All pending items are within the current billing cycle.")

        # 3. SETTLEMENT TABS
        tab_cards, tab_tasks = st.tabs(["💳 Institutional Debt (Cards)", "💸 Direct Settlements (Pix/Cash)"])

        with tab_cards:
            cards_only = unpaid_current[~unpaid_current["Payment Method"].isin(["Pix", "Cash"])]
            if not cards_only.empty:
                card_sums = cards_only.groupby("Payment Method")["Price"].sum().reset_index()

                # Improved Design: Use columns for a "Bank App" look
                cols = st.columns(len(card_sums))
                for i, row in card_sums.iterrows():
                    with cols[i]:
                        # Native English: "Outstanding Balance"
                        st.markdown(f"""
                            <div style="background: rgba(255, 75, 75, 0.1); padding: 15px; border-radius: 10px; border: 1px solid rgba(255, 75, 75, 0.2);">
                                <p style="margin:0; font-size: 0.8rem; color: #94a3b8;">{row['Payment Method']}</p>
                                <h3 style="margin:0; color: #ff4b4b;">R$ {row['Price']:,.2f}</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"Settle {row['Payment Method']}", key=f"btn_settle_{row['Payment Method']}",
                                     use_container_width=True):
                            run_query('UPDATE expenses SET paid = 1 WHERE "Payment Method" = ? AND paid = 0',
                                      (row["Payment Method"],))
                            st.success(f"Account {row['Payment Method']} Cleared!")
                            st.rerun()
            else:
                st.success("All credit accounts are currently in good standing. ✅")

        with tab_tasks:
            pix_cash = unpaid_current[unpaid_current["Payment Method"].isin(["Pix", "Cash"])].copy()
            if not pix_cash.empty:
                # Native English: "Itemized Obligations"
                st.caption("Itemized manual payments requiring verification:")
                pix_cash["Date"] = pix_cash["Date"].dt.date
                pix_cash = pix_cash.sort_values("Date", ascending=True)

                # Security Design: The data_editor acts as our "Audit Log"
                edited_df = st.data_editor(
                    pix_cash[["id", "Date", "Category", "Item", "Price", "paid"]],
                    hide_index=True,
                    use_container_width=True,
                    key="editor_global_pending",
                    column_config={
                        "id": None,
                        "Date": st.column_config.DateColumn("Due Date", format="DD/MM/YYYY"),
                        "Price": st.column_config.NumberColumn("Amount", format="R$ %.2f"),
                        "paid": st.column_config.CheckboxColumn("Settle?")
                    },
                    disabled=["Date", "Category", "Item", "Price"]
                )

                for i in range(len(edited_df)):
                    if edited_df.iloc[i]["paid"] != pix_cash.iloc[i]["paid"]:
                        target_id = int(edited_df.iloc[i]["id"])
                        run_query("UPDATE expenses SET paid = 1 WHERE id = ?", (target_id,))
                        st.toast(f"Verified: {edited_df.iloc[i]['Item']}")
                        st.rerun()
            else:
                st.success("No outstanding manual payments. ✅")
    else:
        # Professional English: "Obligations Cleared"
        st.success("🛡️ **System Status:** All financial obligations have been successfully settled.")

    st.divider()

    # --- TIER 3: SIDE-BY-SIDE LEAKS & BUDGETS ---
    col_leaks, col_budgets = st.columns([1.2, 1])

    with col_leaks:
        # Native English: "Drivers" implies items that move the needle on your finances
        st.markdown("##### 💸 Top Outflow Drivers")

        if not m_exp.empty:
            # 1. DATA PREP: Get the top 5 and calculate their impact
            top_leaks = m_exp.nlargest(5, "Price").copy()
            max_val = top_leaks["Price"].max() if not top_leaks.empty else 1.0

            # 2. UI RENDERING: Use a Data Editor for a more professional, read-only feel
            st.data_editor(
                top_leaks[["Item", "Price", "Category"]],
                hide_index=True,
                use_container_width=True,
                disabled=True,  # Security Engineer Tip: Keep display data read-only
                column_config={
                    "Item": st.column_config.TextColumn("Description"),
                    "Price": st.column_config.ProgressColumn(
                        "Impact",
                        help="Visual weight relative to your highest expense",
                        format="R$ %.2f",
                        min_value=0,
                        max_value=max_val,
                    ),
                    "Category": st.column_config.TextColumn("Tag")
                }
            )
        else:
            st.info("No outflow detected for the current period.")

    with col_budgets:
        st.markdown("##### 🎯 Budget Progress")

        # REFRESH: Pull fresh budget data inside the UI block to ensure it's current
        current_budgets = load_data("budgets")

        # --- DEFENSIVE DATA PREP ---
        # 1. Verify if m_exp exists and has the necessary columns to avoid KeyError
        if not m_exp.empty and "Category" in m_exp.columns and "Price" in m_exp.columns:
            curr_spent = m_exp.groupby("Category")["Price"].sum().reset_index()
            curr_spent["Category"] = curr_spent["Category"].astype(str).str.strip()
        else:
            # Fallback: Create an empty dataframe with correct headers if no data is found
            curr_spent = pd.DataFrame(columns=["Category", "Price"])

        if not current_budgets.empty:
            for _, b_row in current_budgets.iterrows():
                # Standardize names to ensure matching (stripping whitespace)
                cat_name = str(b_row["category"]).strip()

                # Match current category from budget row to the spending dataframe
                spent = curr_spent[curr_spent["Category"] == cat_name]["Price"].sum() if not curr_spent.empty else 0.0

                # 2. Logic Check: Prevent division by zero if budget is 0
                limit = b_row["amount"]
                pct = min(spent / limit, 1.0) if limit > 0 else 0.0

                # --- UI RENDERING ---
                # Professional Formatting: Red if over-budget, Blue if healthy
                color = "#ef4444" if pct >= 1.0 else "#3b82f6"

                st.markdown(f"""
                    <div style="margin-bottom: 5px;">
                        <small style="color: #94a3b8;">{cat_name}</small>
                        <small style="float: right; color: {color}; font-weight: bold;">
                            R$ {spent:,.0f} / R$ {limit:,.0f}
                        </small>
                    </div>
                """, unsafe_allow_html=True)
                st.progress(pct)
        else:
            st.info("No budgets defined. Head to 'Set Budgets' to begin.")


    # --- TIER 4: INTELLIGENCE HUB ---
    st.divider()
    st.markdown("### 🕵️‍♂️ Intelligence Hub")

    with st.expander("🔍 Deep Data Analysis", expanded=False):
        date_range = st.date_input("Analysis Period", value=(dt_class.today().replace(day=1), dt_class.today()))

        if len(date_range) == 2:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

            # Comparison Fix: Convert DB strings to datetime for accurate filtering
            p_exp = df_exp_all.copy()
            p_exp["Date"] = pd.to_datetime(p_exp["Date"])
            p_exp = p_exp[(p_exp["Date"] >= start) & (p_exp["Date"] <= end)] if not p_exp.empty else pd.DataFrame()

            p_inc = df_inc_all.copy()
            p_inc["Date"] = pd.to_datetime(p_inc["Date"])
            p_inc = p_inc[(p_inc["Date"] >= start) & (p_inc["Date"] <= end)] if not p_inc.empty else pd.DataFrame()

            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("##### Momentum")
                combined = pd.DataFrame()
                if not p_exp.empty:
                    e = p_exp.groupby(p_exp["Date"].dt.to_period("M").astype(str))["Price"].sum().reset_index(
                        name="Price")
                    e["Type"] = "Expense";
                    combined = pd.concat([combined, e])
                if not p_inc.empty:
                    i = p_inc.groupby(p_inc["Date"].dt.to_period("M").astype(str))["Price"].sum().reset_index(
                        name="Price")
                    i["Type"] = "Income";
                    combined = pd.concat([combined, i])

                if not combined.empty:
                    st.plotly_chart(
                        px.bar(combined, x="Date", y="Price", color="Type", barmode="group", template="plotly_dark",
                               color_discrete_map={"Income": "#10b981", "Expense": "#ef4444"}),
                        use_container_width=True)

            with c2:
                st.markdown("##### Category Mix")
                if not p_exp.empty:
                    st.plotly_chart(px.pie(p_exp, values="Price", names="Category", hole=0.6, template="plotly_dark"),
                                    use_container_width=True)

            if not p_exp.empty:
                st.markdown("##### 📊 Statistical Summary")
                stats = p_exp.groupby("Category")["Price"].agg(['sum', 'count', 'mean']).rename(
                    columns={'sum': 'Total', 'count': 'Logs', 'mean': 'Avg'}).sort_values('Total', ascending=False)
                st.dataframe(stats, column_config={"Total": st.column_config.NumberColumn(format="R$ %.2f"),
                                                   "Avg": st.column_config.NumberColumn(format="R$ %.2f")},
                             use_container_width=True)

    # --- TIER 5: NOTIFICATIONS ---
    st.divider()
    with st.expander("📧 Notification Center"):
        col_notif1, col_notif2 = st.columns([2, 1])
        user_email = col_notif1.text_input("Report Recipient", placeholder="your@email.com")
        if col_notif2.button("📧 Dispatch Monthly Report"):
            if user_email:
                report_body = generate_monthly_summary_text()
                if db_utils.send_financial_report(user_email, "Financial Summary", report_body):
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
    expense_cats = df_cats_local[df_cats_local['type'] == 'Expense']['name'].tolist()

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
                rows = generate_installments(d, item, pr, cat, meth, inst)
                conn = get_connection()
                conn.cursor().executemany(
                    'INSERT INTO expenses (Date, Category, Item, Price, "Payment Method", paid) VALUES (?, ?, ?, ?, ?, ?)',
                    rows)
                conn.commit()
                st.toast("Logged!", icon="✅")
                st.rerun()

    st.divider()

    with st.expander("✏️ Correct Expense History (Ledger Mode)"):
        st.info("Edit cells below to fix typos or wrong values. Changes save instantly.")
        df_edit_exp = load_data("expenses")  # Ensure it's not the filtered one
        edited_exp = st.data_editor(df_edit_exp, key="ledger_exp_page", hide_index=True, use_container_width=True)
        if not edited_exp.equals(df_edit_exp):
            for i in range(len(edited_exp)):
                if not edited_exp.iloc[i].equals(df_edit_exp.iloc[i]):
                    row = edited_exp.iloc[i]
                    run_query("""UPDATE expenses
                                 SET Date=?,
                                     Category=?,
                                     Item=?,
                                     Price=?,
                                     "Payment Method"=?
                                 WHERE id = ?""",
                              (row["Date"], row["Category"], row["Item"], row["Price"], row["Payment Method"],
                               int(row["id"])))
                    st.toast("Updated!");
                    st.rerun()

    st.divider()
    st.markdown("### 📜 History & Maintenance")

    # Refresh data for the table
    df_exp_all = load_data("expenses")

    if not df_exp_all.empty:
        cv, cd = st.columns([3, 1])
        with cv:
            st.dataframe(
                df_exp_all.sort_values("Date", ascending=False),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                    "Price": st.column_config.NumberColumn("Price", format="R$ %.2f")
                }
            )
        with cd:
            st.markdown("🗑️ **Delete Record**")
            # This remains the same, but now it uses the single physical 'id' column
            target = st.selectbox("Select ID", (df_exp_all["id"].astype(str) + " - " + df_exp_all["Item"]).tolist(),
                                  key="del_exp")
            if st.button("Delete Permanently"):
                run_query("DELETE FROM expenses WHERE id = ?", (target.split(" - ")[0],))
                st.rerun()



# ==============================================================================
# PAGE 3: INCOMES
# ==============================================================================
elif page == "💰 Incomes":
    st.markdown("## 💰 Income Streams")

    # 1. FETCH LATEST CATEGORIES (The Fix for Dynamic Sync)
    df_cats_local = load_data("categories")
    income_cats = df_cats_local[df_cats_local['type'] == 'Income']['name'].tolist()

    # Fallback in case the category table is empty
    if not income_cats:
        income_cats = ["Salary", "Freelance", "Dividends"]

    with st.form("income_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        date = c1.date_input("Date")

        # USE THE DYNAMIC LIST HERE
        category = c2.selectbox("Category", income_cats)

        price = c3.number_input("Amount", step=0.01)
        item = st.text_input("Description")

        if st.form_submit_button("Save Income"):
            run_query("INSERT INTO incomes (Date, Category, Item, Price) VALUES (?, ?, ?, ?)",
                      (date, category, item, price))
            st.rerun()

    st.divider()
    with st.expander("✏️ Correct Income History (Ledger Mode)"):
        df_edit_inc = load_data("incomes")
        edited_inc = st.data_editor(df_edit_inc, key="ledger_inc_page", hide_index=True, use_container_width=True)
        if not edited_inc.equals(df_edit_inc):
            for i in range(len(edited_inc)):
                if not edited_inc.iloc[i].equals(df_edit_inc.iloc[i]):
                    row = edited_inc.iloc[i]
                    run_query("""UPDATE incomes
                                 SET Date=?,
                                     Category=?,
                                     Item=?,
                                     Price=?
                                 WHERE id = ?""",
                              (row["Date"], row["Category"], row["Item"], row["Price"], int(row["id"])))
                    st.toast("Updated!");
                    st.rerun()
    st.divider()
    st.markdown("### 📜 History & Maintenance")

    # 2. LOAD DATA
    df_inc_all = load_data("incomes")

    if not df_inc_all.empty:
        col_view, col_del = st.columns([3, 1])
        with col_view:
            st.dataframe(
                df_inc_all.sort_values(by="Date", ascending=False),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                    "Price": st.column_config.NumberColumn("Amount", format="R$ %.2f")
                }
            )
        with col_del:
            st.markdown("🗑️ **Delete Income**")
            # Ensure we are using the single physical 'id' column
            options = (df_inc_all["id"].astype(str) + " - " + df_inc_all["Item"]).tolist()
            target = st.selectbox("Select ID", options, key="del_inc_ui")

            if st.button("Confirm Delete"):
                # Change 'rowid' to 'id' here since the table has a physical ID column
                run_query("DELETE FROM incomes WHERE id = ?", (target.split(" - ")[0],))
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

    with st.form("recurring_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        item_name = c1.text_input("Service/Item (e.g. Netflix, Rent)")
        price = c2.number_input("Monthly Price", min_value=0.0, step=0.01)

        c3, c4 = st.columns(2)
        category = c3.selectbox("Category", ["Housing", "Fun", "Transport", "Food", "Educação"])
        day = c4.number_input("Due Day of Month", 1, 31, 1)

        if st.form_submit_button("Add Subscription"):
            if item_name and price > 0:
                run_query(
                    "INSERT INTO recurring (item, category, price, payment_method, day_of_month, active) VALUES (?, ?, ?, 'Pix', ?, 1)",
                    (item_name, category, price, int(day)))
                st.success(f"Subscription for {item_name} active!")
                st.rerun()

    st.divider()
    df_rec = load_data("recurring")
    if not df_rec.empty:
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

            # --- NEW DELETE OPTION ---
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
if page == "📈 Wealth Command":
    st.title("📈 Wealth Command & FIRE Strategy")
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