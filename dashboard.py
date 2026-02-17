import streamlit as st
import pandas as pd
import os
import plotly.express as px
from dateutil.relativedelta import relativedelta
from datetime import date as dt_class

# --- CONFIGURATION ---
st.set_page_config(page_title="My Financial Core", page_icon="💰", layout="wide")
FINANCE_FILE = "finance.csv"
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
    "💳 Manage Cards",
    "💰 Incomes (Coming Soon)"
])

# ==============================================================================
# PAGE 1: DASHBOARD (Read-Only Analytics)
# ==============================================================================
if page == "📊 Dashboard":
    st.title("📊 Executive Dashboard")
    st.markdown("### Overview of your Financial Health")

    if os.path.exists(FINANCE_FILE):
        df = pd.read_csv(FINANCE_FILE)
        df["Date"] = pd.to_datetime(df["Date"])

        # 1. BIG METRICS
        current_month = dt_class.today().strftime("%Y-%m")
        df["Month"] = df["Date"].dt.to_period("M").astype(str)

        # Calculate spending specifically for THIS month
        this_month_expenses = df[df["Month"] == current_month]["Price"].sum()
        total_all_time = df["Price"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Spent This Month", f"R$ {this_month_expenses:,.2f}")
        col2.metric("Total All Time", f"R$ {total_all_time:,.2f}")
        col3.metric("Active Cards", len(load_data(CARDS_FILE, ["Card Name"])))

        st.divider()

        # 2. CHARTS (Side by Side)
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("📅 Monthly Cash Flow")
            # Group by Month for the Bar Chart
            monthly_data = df.groupby("Month")["Price"].sum().reset_index()
            fig_bar = px.bar(monthly_data, x="Month", y="Price", text_auto='.2s', title="Future Commitments")
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            st.subheader("🍕 Category Breakdown")
            # Pie Chart for Categories
            category_data = df.groupby("Category")["Price"].sum().reset_index()
            fig_pie = px.pie(category_data, values="Price", names="Category", title="Where is money going?")
            st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.info("No data available yet. Go to 'Expenses' to add your first transaction.")

# ==============================================================================
# PAGE 2: EXPENSES (Entry & Management)
# ==============================================================================
elif page == "💸 Expenses (Entry)":
    st.title("💸 Expenses Management")

    # --- SECTION A: NEW ENTRY FORM ---
    st.markdown("### 📝 Add New Expense")
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

        if st.form_submit_button("💾 Save Expense"):
            if price > 0 and item:
                new_df = generate_installments(date, item, price, category, method, installments)
                if os.path.exists(FINANCE_FILE):
                    new_df.to_csv(FINANCE_FILE, mode='a', header=False, index=False)
                else:
                    new_df.to_csv(FINANCE_FILE, index=False)
                st.success("Expense Saved!")
                st.rerun()

    st.divider()

    # --- SECTION B: HISTORY & FILTER ---
    st.markdown("### 🔍 Transaction History")

    if os.path.exists(FINANCE_FILE):
        df = pd.read_csv(FINANCE_FILE)
        df["Date"] = pd.to_datetime(df["Date"])

        # Filters in an Expander to keep it clean
        with st.expander("Filter Options", expanded=True):
            col_f1, col_f2 = st.columns(2)
            start_date = col_f1.date_input("Start Date", dt_class.today() - relativedelta(months=1))
            end_date = col_f2.date_input("End Date", dt_class.today() + relativedelta(months=6))

            cats = ["All"] + df["Category"].unique().tolist()
            sel_cat = st.selectbox("Filter Category", cats)

        # Apply Logic
        mask = (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)
        filtered_df = df.loc[mask]

        if sel_cat != "All":
            filtered_df = filtered_df[filtered_df["Category"] == sel_cat]

        filtered_df = filtered_df.sort_values(by="Date", ascending=False)

        # Editable Table
        edited_df = st.data_editor(filtered_df, use_container_width=True, num_rows="dynamic", key="history")

        if st.button("Update Database with Changes"):
            # Note: A real app needs complex logic to update specific rows.
            # For now, we block this on filters for safety, or we'd overwrite the whole DB with just the filtered view.
            if sel_cat != "All" or start_date > (dt_class.today() - relativedelta(years=5)):
                st.warning(
                    "⚠️ Safety Lock: You can only save edits when viewing ALL data (no filters). This prevents data loss.")
            else:
                edited_df.to_csv(FINANCE_FILE, index=False)
                st.success("Updated!")

# ==============================================================================
# PAGE 3: MANAGE CARDS
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

# ==============================================================================
# PAGE 4: INCOMES (Placeholder)
# ==============================================================================
elif page == "💰 Incomes (Coming Soon)":
    st.title("💰 Income Management")
    st.info("🚧 Under Construction: This is where you will add Salaries, Dividends, and Freelance work.")