import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from dateutil.relativedelta import relativedelta
from datetime import date as dt_class
from db_utils import *

# --- UI HELPER FUNCTIONS ---
def metric_card(label, value, prefix="R$ "):
    """Renders a clean, modern metric card using HTML/CSS."""
    st.markdown(f"""
    <div class="fintech-card" style="padding: 15px; text-align: center;">
        <p style="color: #8B949E; font-size: 12px; margin:0; text-transform: uppercase;">{label}</p>
        <h2 style="margin:0; border:none; font-size: 24px;">{prefix}{value:,.2f}</h2>
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


# --- 4. DATA ENGINE (FIXED ID LOADER) ---
def get_connection():
    return sqlite3.connect(DB_NAME)

def load_data(table_name):
    """Standard loader for configuration tables."""
    with get_connection() as conn:
        try:
            return pd.read_sql(f"SELECT * FROM {table_name}", conn)
        except:
            return pd.DataFrame()

def load_data_with_id(table_name):
    """Special loader for Incomes/Expenses: FORCES 'rowid' to act as 'id'."""
    with get_connection() as conn:
        try:
            return pd.read_sql(f"SELECT rowid as id, * FROM {table_name}", conn)
        except:
            return pd.DataFrame()

def run_query(query, params=()):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

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

    # --- 1. DATA PREP ---
    curr_month_str = dt_class.today().strftime("%Y-%m")
    today_str = dt_class.today().strftime("%Y-%m-%d")

    m_exp = df_exp_all[pd.to_datetime(df_exp_all["Date"]).dt.strftime(
        "%Y-%m") == curr_month_str] if not df_exp_all.empty else pd.DataFrame()
    m_inc = df_inc_all[pd.to_datetime(df_inc_all["Date"]).dt.strftime(
        "%Y-%m") == curr_month_str] if not df_inc_all.empty else pd.DataFrame()

    income_val = m_inc["Price"].sum() if not m_inc.empty else 0.0
    expense_val = m_exp["Price"].sum() if not m_exp.empty else 0.0

    total_cash = (df_inc_all["Price"].sum() if not df_inc_all.empty else 0) - (
        df_exp_all["Price"].sum() if not df_exp_all.empty else 0)
    total_invested = df_inv["Amount"].sum() if not df_inv.empty else 0
    net_worth = total_cash + total_invested

    # --- TIER 0: EXECUTIVE SUMMARY ---
    st.markdown("## 🏛️ Executive Summary")

    # Custom CSS for the "Value Blocks"
    st.markdown("""
        <style>
        .main-card {
            background-color: #1a1c24;
            padding: 20px;
            border-radius: 15px;
            border-top: 4px solid #3b82f6;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .metric-label { color: #94a3b8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; }
        .metric-value { color: #f8fafc; font-size: 1.6rem; font-weight: 700; margin: 0; }
        </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="main-card"><p class="metric-label">Liquid Cash</p><p class="metric-value">R$ {total_cash:,.2f}</p></div>',
            unsafe_allow_html=True)
    with c2:
        st.markdown(
            f'<div class="main-card" style="border-top-color: #8b5cf6;"><p class="metric-label">Investments</p><p class="metric-value">R$ {total_invested:,.2f}</p></div>',
            unsafe_allow_html=True)
    with c3:
        st.markdown(
            f'<div class="main-card" style="border-top-color: #10b981;"><p class="metric-label">Net Worth</p><p class="metric-value">R$ {net_worth:,.2f}</p></div>',
            unsafe_allow_html=True)

    st.divider()

    # --- TIER 1: MONTHLY PERFORMANCE ---
    st.markdown("## 🗓️ Monthly Flow")

    savings_val = income_val - expense_val
    savings_pct = (savings_val / income_val * 100) if income_val > 0 else 0
    burn_rate = (expense_val / income_val * 100) if income_val > 0 else 0

    mc1, mc2, mc3 = st.columns(3)
    # Style these with containers for better alignment
    with mc1:
        st.markdown(
            f'<div style="background: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #10b981;">'
            f'<p style="color: #10b981; font-weight: bold; margin:0;">+ Income</p><h3 style="margin:0;">R$ {income_val:,.2f}</h3></div>',
            unsafe_allow_html=True)
    with mc2:
        st.markdown(
            f'<div style="background: rgba(239, 68, 68, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #ef4444;">'
            f'<p style="color: #ef4444; font-weight: bold; margin:0;">- Expenses</p><h3 style="margin:0;">R$ {expense_val:,.2f}</h3><small>Burn Rate: {burn_rate:.1f}%</small></div>',
            unsafe_allow_html=True)
    with mc3:
        st.markdown(
            f'<div style="background: rgba(59, 130, 246, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #3b82f6;">'
            f'<p style="color: #3b82f6; font-weight: bold; margin:0;">= Margin</p><h3 style="margin:0;">R$ {savings_val:,.2f}</h3><small>Savings Rate: {savings_pct:.1f}%</small></div>',
            unsafe_allow_html=True)

    # --- TIER 2: CONTROL CENTER ---
    st.divider()
    st.markdown("### 🚩 Control Center")

    # 1. Fetch Global Unpaid Data for the middle block
    # We filter the all-time dataframe for any status that means "not paid"
    if not df_exp_all.empty:
        unpaid_global_df = df_exp_all[df_exp_all["paid"].isin([0, False, "0"])]
        pending_global_val = unpaid_global_df["Price"].sum()
    else:
        pending_global_val = 0.0

    # 2. Logic for Monthly Liquid Control
    # Already Settled: Only what was paid THIS MONTH (Matches Tier 1)
    paid_mtd = m_exp[m_exp["paid"] == 1]["Price"].sum() if not m_exp.empty else 0.0

    # Cash Remaining: Total Monthly Income minus what actually left the account (Paid)
    cash_remaining = income_val - paid_mtd

    # 3. Design Blocks
    cc1, cc2, cc3 = st.columns(3)

    with cc1:
        st.markdown(f'''
            <div style="background: rgba(16, 185, 129, 0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(16, 185, 129, 0.2); border-top: 4px solid #10b981;">
                <p style="color: #10b981; font-weight: bold; margin:0; font-size: 0.8rem;">ALREADY SETTLED (MTD)</p>
                <h3 style="margin:0; font-size: 1.4rem;">R$ {paid_mtd:,.2f}</h3>
            </div>
        ''', unsafe_allow_html=True)

    with cc2:
        # UPDATED: This now shows Global Debt (Past + Present)
        st.markdown(f'''
            <div style="background: rgba(245, 158, 11, 0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(245, 158, 11, 0.2); border-top: 4px solid #f59e0b;">
                <p style="color: #f59e0b; font-weight: bold; margin:0; font-size: 0.8rem;">TOTAL PENDING (GLOBAL)</p>
                <h3 style="margin:0; font-size: 1.4rem;">R$ {pending_global_val:,.2f}</h3>
            </div>
        ''', unsafe_allow_html=True)

    with cc3:
        st.markdown(f'''
            <div style="background: rgba(59, 130, 246, 0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(59, 130, 246, 0.2); border-top: 4px solid #3b82f6;">
                <p style="color: #3b82f6; font-weight: bold; margin:0; font-size: 0.8rem;">CASH REMAINING</p>
                <h3 style="margin:0; font-size: 1.4rem;">R$ {cash_remaining:,.2f}</h3>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- PENDING ACTIONS TABS ---

    # 1. Use the main dataframe (df_exp_all) which we know is working
    if not df_exp_all.empty:
        # Filter for EVERYTHING unpaid (0, False, or "0")
        unpaid_all_time = df_exp_all[df_exp_all["paid"].isin([0, False, "0"])]
    else:
        unpaid_all_time = pd.DataFrame()

    # 2. RENDER TABS
    if not unpaid_all_time.empty:
        tab_cards, tab_tasks = st.tabs(["💳 Credit Card Balances", "💸 Manual Payments"])

        with tab_cards:
            # Filter for anything NOT Pix or Cash
            cards_only = unpaid_all_time[~unpaid_all_time["Payment Method"].isin(["Pix", "Cash"])]

            if not cards_only.empty:
                card_sums = cards_only.groupby("Payment Method")["Price"].sum().reset_index()
                cols = st.columns(len(card_sums))
                for i, row in card_sums.iterrows():
                    with cols[i]:
                        st.metric(row["Payment Method"], f"R$ {row['Price']:,.2f}")
                        # Unique key to prevent Streamlit errors
                        if st.button(f"Settle {row['Payment Method']}", key=f"btn_settle_{row['Payment Method']}"):
                            run_query('UPDATE expenses SET paid = 1 WHERE "Payment Method" = ? AND paid = 0',
                                      (row["Payment Method"],))
                            st.success(f"Settled {row['Payment Method']}!")
                            st.rerun()
            else:
                st.success("All credit cards clear! ✅")

        with tab_tasks:
            # Filter for Pix and Cash
            pix_cash = unpaid_all_time[unpaid_all_time["Payment Method"].isin(["Pix", "Cash"])].copy()

            if not pix_cash.empty:
                st.info("Check boxes to settle individual items.")
                # Standardize date for sorting
                pix_cash["Date"] = pd.to_datetime(pix_cash["Date"]).dt.date
                pix_cash = pix_cash.sort_values("Date", ascending=True)

                edited_df = st.data_editor(
                    pix_cash[["id", "Date", "Category", "Item", "Price", "paid"]],
                    hide_index=True,
                    use_container_width=True,
                    key="editor_global_pending",
                    column_config={
                        "id": None,
                        "Date": st.column_config.DateColumn("Due Date", format="DD/MM/YYYY"),
                        "Price": st.column_config.NumberColumn("Amount", format="R$ %.2f"),
                        "paid": st.column_config.CheckboxColumn("Done?")
                    },
                    disabled=["Date", "Category", "Item", "Price"]
                )

                # Logic to detect the checkmark
                for i in range(len(edited_df)):
                    if edited_df.iloc[i]["paid"] != pix_cash.iloc[i]["paid"]:
                        target_id = int(edited_df.iloc[i]["id"])
                        run_query("UPDATE expenses SET paid = 1 WHERE id = ?", (target_id,))
                        st.toast(f"Updated {edited_df.iloc[i]['Item']}!")
                        st.rerun()
            else:
                st.success("Manual payments clear! ✅")
    else:
        st.success("✅ No pending obligations found in the database.")

    # --- TIER 3: SIDE-BY-SIDE LEAKS & BUDGETS ---
    col_leaks, col_budgets = st.columns([1.2, 1])

    with col_leaks:
        st.markdown("##### 💸 Top 5 Leaks")
        if not m_exp.empty:
            top_leaks = m_exp.nlargest(5, "Price")[["Item", "Price", "Category"]]
            st.dataframe(top_leaks, column_config={"Price": st.column_config.NumberColumn(format="R$ %.2f")},
                         hide_index=True, use_container_width=True)

    with col_budgets:
        st.markdown("##### 🎯 Budget Progress")
        if not df_budgets.empty:
            curr_spent = m_exp.groupby("Category")["Price"].sum().reset_index()
            for _, b_row in df_budgets.iterrows():
                spent = curr_spent[curr_spent["Category"] == b_row["category"]][
                    "Price"].sum() if not curr_spent.empty else 0.0
                pct = min(spent / b_row["amount"], 1.0) if b_row["amount"] > 0 else 0
                st.markdown(f"<small>{b_row['category']} (R$ {spent:,.0f} / R$ {b_row['amount']:,.0f})</small>",
                            unsafe_allow_html=True)
                st.progress(pct)


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
                if send_financial_report(user_email, "Financial Summary", report_body):
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
    with st.form("budget_form"):
        cats = ["Food", "Transport", "Housing", "Fun", "Investments"]
        new_b = {}
        for c in cats:
            existing = df_budgets[df_budgets['category'] == c]['amount'].values
            new_b[c] = st.number_input(f"Limit for {c}", value=float(existing[0]) if len(existing) > 0 else 0.0)
        if st.form_submit_button("Update Budgets"):
            for c, a in new_b.items(): run_query("INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)",
                                                 (c, a)); st.rerun()
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

    # THE FORM (Missing in previous snippet)
    with st.form("recurring_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        item_name = c1.text_input("Service/Item (e.g. Netflix, Rent)")
        price = c2.number_input("Monthly Price", min_value=0.0, step=0.01)

        c3, c4 = st.columns(2)
        category = c3.selectbox("Category", ["Housing", "Fun", "Transport", "Food", "Educação"])
        day = c4.number_input("Due Day of Month", 1, 31, 1)

        if st.form_submit_button("Add Subscription"):
            if item_name and price > 0:
                # We insert with active=1 by default
                run_query(
                    "INSERT INTO recurring (item, category, price, payment_method, day_of_month, active) VALUES (?, ?, ?, 'Pix', ?, 1)",
                    (item_name, category, price, int(day)))
                st.success(f"Subscription for {item_name} active!")
                st.rerun()

    st.divider()
    df_rec = load_data("recurring")
    if not df_rec.empty:
        col_view, col_status = st.columns([3, 1])
        with col_view:
            st.dataframe(df_rec, use_container_width=True, hide_index=True)
        with col_status:
            st.markdown("⚙️ **Subscription Status**")
            options = (df_rec["id"].astype(str) + " - " + df_rec["item"]).tolist()
            target = st.selectbox("Select Service", options, key="status_rec_ui")

            if st.button("Activate/Resume"):
                run_query("UPDATE recurring SET active = 1 WHERE id = ?", (target.split(" - ")[0],))
                st.rerun()
            if st.button("Inactivate/Pause"):
                run_query("UPDATE recurring SET active = 0 WHERE id = ?", (target.split(" - ")[0],))
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