import streamlit as st
import pandas as pd
import os
import plotly.express as px
from dateutil.relativedelta import relativedelta
from datetime import date as dt_class

# --- CONFIGURATION ---
st.set_page_config(page_title="My Financial Core", page_icon="💰", layout="wide")
FINANCE_FILE = "finance.csv"
INCOME_FILE = "incomes.csv"  # <--- NEW DATABASE
CARDS_FILE = "cards.csv"


# --- HELPER FUNCTIONS ---
def load_data(file_path, columns):
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=columns)


def save_data(df, file_path):
    df.to_csv(file_path, index=False)


def generate_installments(date, item, price, category, payment_method, installments):
    new_rows = []
    cards_df = load_data(CARDS_FILE, ["Card Name", "Closing Day", "Due Day"])
    card_rule = cards_df[cards_df["Card Name"] == payment_method]
    is_credit_card = not card_rule.empty

    for i in range(installments):
        if is_credit_card:
            closing_day = int(card_rule.iloc[0]["Closing Day"])
            due_day = int(card_rule.iloc[0]["Due Day"])
            months_to_add = i
            if date.day > closing_day:
                months_to_add += 1
            future_date = date + relativedelta(months=months_to_add)
            try:
                final_date = future_date.replace(day=due_day)
            except ValueError:
                final_date = future_date + relativedelta(day=31)
            row_date = final_date
        else:
            row_date = date + relativedelta(months=i)

        item_name = f"{item} ({i + 1}/{installments})" if installments > 1 else item
        item_price = round(price / installments, 2)
        new_rows.append({
            "Date": row_date,
            "Category": category,
            "Item": item_name,
            "Price": item_price,
            "Payment Method": payment_method
        })
    return pd.DataFrame(new_rows)


# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "📊 Dashboard",
    "💸 Expenses (Entry)",
    "💰 Incomes (Entry)",
    "💳 Manage Cards"
])

# ==============================================================================
# PAGE 1: DASHBOARD (THE CFO VIEW)
# ==============================================================================
if page == "📊 Dashboard":
    st.title("📊 Executive Dashboard")

    # 1. LOAD DATA
    df_expenses = load_data(FINANCE_FILE, ["Date", "Price"])
    df_income = load_data(INCOME_FILE, ["Date", "Price"])

    if not df_expenses.empty:
        df_expenses["Date"] = pd.to_datetime(df_expenses["Date"])
        # Fix: Only convert to datetime if data exists
        if not df_income.empty:
            df_income["Date"] = pd.to_datetime(df_income["Date"])

        # 2. DATE FILTER (THIS MONTH)
        current_month = dt_class.today().strftime("%Y-%m")

        # Filter Expenses
        df_expenses["Month"] = df_expenses["Date"].dt.to_period("M").astype(str)
        total_expenses = df_expenses[df_expenses["Month"] == current_month]["Price"].sum()

        # Filter Income (Handle empty income file safely)
        total_income = 0.0
        if not df_income.empty:
            df_income["Month"] = df_income["Date"].dt.to_period("M").astype(str)
            total_income = df_income[df_income["Month"] == current_month]["Price"].sum()

        # 3. CALCULATE SAVINGS
        savings = total_income - total_expenses

        # 4. DISPLAY METRICS (KPIs)
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Income (This Month)", f"R$ {total_income:,.2f}")
        col2.metric("💸 Expenses (This Month)", f"R$ {total_expenses:,.2f}", delta_color="inverse")
        col3.metric("🐷 Net Savings", f"R$ {savings:,.2f}", delta=f"{savings:,.2f}")

        st.divider()

        # 5. CHARTS
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Monthly Cash Flow")
            # Group Expenses
            exp_monthly = df_expenses.groupby("Month")["Price"].sum().reset_index()
            exp_monthly["Type"] = "Expense"

            # Group Income
            if not df_income.empty:
                inc_monthly = df_income.groupby("Month")["Price"].sum().reset_index()
                inc_monthly["Type"] = "Income"
                # Combine both for a clustered bar chart
                combined_df = pd.concat([exp_monthly, inc_monthly])
                fig_bar = px.bar(combined_df, x="Month", y="Price", color="Type", barmode="group",
                                 title="Income vs Expenses")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Add Income to see the comparison chart.")

        with c2:
            st.subheader("Expense Breakdown")
            cat_data = df_expenses.groupby("Category")["Price"].sum().reset_index()
            fig_pie = px.pie(cat_data, values="Price", names="Category", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.info("No data yet. Go to 'Expenses' or 'Incomes' to start.")

# ==============================================================================
# PAGE 2: EXPENSES
# ==============================================================================
elif page == "💸 Expenses (Entry)":
    st.title("💸 Expenses Management")
    # ... (Same as before) ...
    df_cards = load_data(CARDS_FILE, ["Card Name"])
    payment_options = ["Pix", "Cash"] + df_cards["Card Name"].tolist()

    with st.form("entry_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        date = c1.date_input("Date")
        item = c1.text_input("Item")
        category = c2.selectbox("Category", ["Food", "Transport", "Housing", "Fun", "Investments"])
        price = c2.number_input("Price", step=0.01)
        method = c3.selectbox("Payment", payment_options)
        installments = c4.number_input("Installments", 1, 24, 1)

        if st.form_submit_button("Save Expense"):
            if price > 0 and item:
                new_df = generate_installments(date, item, price, category, method, installments)
                if os.path.exists(FINANCE_FILE):
                    new_df.to_csv(FINANCE_FILE, mode='a', header=False, index=False)
                else:
                    new_df.to_csv(FINANCE_FILE, index=False)
                st.success("Expense Saved!")
                st.rerun()

    st.divider()
    if os.path.exists(FINANCE_FILE):
        df = pd.read_csv(FINANCE_FILE)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by="Date", ascending=False)
        st.data_editor(df, use_container_width=True, num_rows="dynamic", key="exp_history")
        if st.button("Update Expenses"):
            df.to_csv(FINANCE_FILE, index=False)  # Simplified save for now

# ==============================================================================
# PAGE 3: INCOMES (NEW!)
# ==============================================================================
elif page == "💰 Incomes (Entry)":
    st.title("💰 Income Management")
    st.markdown("### 💵 Add New Income")

    with st.form("income_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        date = c1.date_input("Date Received")
        category = c2.selectbox("Category", ["Salary", "Freelance", "Dividends", "Gift", "Other"])
        price = c3.number_input("Amount (R$)", step=0.01)
        item = st.text_input("Description (e.g. Salary February)")

        if st.form_submit_button("Save Income"):
            if price > 0:
                new_data = pd.DataFrame({
                    "Date": [date],
                    "Category": [category],
                    "Item": [item],
                    "Price": [price]
                })
                if os.path.exists(INCOME_FILE):
                    new_data.to_csv(INCOME_FILE, mode='a', header=False, index=False)
                else:
                    new_data.to_csv(INCOME_FILE, index=False)
                st.success("Income Saved!")
                st.rerun()

    st.divider()
    st.markdown("### 📜 Income History")
    if os.path.exists(INCOME_FILE):
        df = pd.read_csv(INCOME_FILE)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by="Date", ascending=False)

        edited_income = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="inc_history")
        if st.button("Update Income DB"):
            edited_income.to_csv(INCOME_FILE, index=False)
            st.success("Updated!")
            st.rerun()

# ==============================================================================
# PAGE 4: MANAGE CARDS
# ==============================================================================
elif page == "💳 Manage Cards":
    st.title("💳 Manage Cards")
    with st.form("card_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Card Name")
        closing = c2.number_input("Closing Day", 1, 31)
        due = c3.number_input("Due Day", 1, 31)
        if st.form_submit_button("Save Card"):
            if name:
                df_cards = load_data(CARDS_FILE, ["Card Name", "Closing Day", "Due Day"])
                new_card = pd.DataFrame({"Card Name": [name], "Closing Day": [closing], "Due Day": [due]})
                save_data(pd.concat([df_cards, new_card], ignore_index=True), CARDS_FILE)
                st.success("Card Added!")
                st.rerun()
    st.divider()
    df_cards = load_data(CARDS_FILE, ["Card Name", "Closing Day", "Due Day"])
    if not df_cards.empty:
        st.data_editor(df_cards, num_rows="dynamic")