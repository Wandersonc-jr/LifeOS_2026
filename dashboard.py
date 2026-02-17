import streamlit as st
import pandas as pd
import os
import plotly.express as px
from dateutil.relativedelta import relativedelta  # New Math Tool!

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


# --- THE TIME MACHINE (LOGIC ENGINE) ---
def generate_installments(date, item, price, category, payment_method, installments):
    new_rows = []

    # 1. Get Card Rules (if it's a credit card)
    cards_df = load_data(CARDS_FILE, ["Card Name", "Closing Day", "Due Day"])
    card_rule = cards_df[cards_df["Card Name"] == payment_method]

    is_credit_card = not card_rule.empty

    # 2. Loop through installments (1 to N)
    for i in range(installments):
        current_date = date

        # LOGIC: Credit Card Date Calculation
        if is_credit_card:
            closing_day = int(card_rule.iloc[0]["Closing Day"])
            due_day = int(card_rule.iloc[0]["Due Day"])

            # Base logic: If purchase is AFTER closing, bump to next month
            # We also add 'i' months for the installments loop
            months_to_add = i
            if date.day > closing_day:
                months_to_add += 1

            # Calculate the target month/year
            future_date = date + relativedelta(months=months_to_add)

            # Set the exact Due Day
            # (Handle short months like Feb: if Due Day is 30, it clamps to 28)
            try:
                final_date = future_date.replace(day=due_day)
            except ValueError:
                # Fallback for Feb 30 -> Feb 28
                final_date = future_date + relativedelta(day=31)

            row_date = final_date

        else:
            # Simple Logic (Pix/Cash): Just add months if it's recurrent, or keep same date
            # For now, let's assume Pix installments are monthly too (like a recurrent bill)
            row_date = date + relativedelta(months=i)

        # 3. Create the Row
        # If installments > 1, add (1/10) to the name
        item_name = f"{item} ({i + 1}/{installments})" if installments > 1 else item
        item_price = price / installments  # Split the price!

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
page = st.sidebar.radio("Go to", ["📊 Dashboard", "💳 Manage Cards"])

# ==============================================================================
# PAGE 1: MANAGE CARDS
# ==============================================================================
if page == "💳 Manage Cards":
    st.title("💳 Manage Credit Cards")

    with st.form("add_card_form"):
        col1, col2, col3 = st.columns(3)
        name = col1.text_input("Card Name")
        closing_day = col2.number_input("Closing Day", 1, 31)
        due_day = col3.number_input("Due Day", 1, 31)
        if st.form_submit_button("Save Card"):
            if name:
                df_cards = load_data(CARDS_FILE, ["Card Name", "Closing Day", "Due Day"])
                new_card = pd.DataFrame({"Card Name": [name], "Closing Day": [closing_day], "Due Day": [due_day]})
                save_data(pd.concat([df_cards, new_card], ignore_index=True), CARDS_FILE)
                st.success(f"Card '{name}' saved!")
                st.rerun()

    st.divider()
    df_cards = load_data(CARDS_FILE, ["Card Name", "Closing Day", "Due Day"])
    if not df_cards.empty:
        st.data_editor(df_cards, key="card_editor", num_rows="dynamic")

# ==============================================================================
# PAGE 2: DASHBOARD
# ==============================================================================
elif page == "📊 Dashboard":
    st.title("My Financial Core 💰")

    # Load Card Options
    df_cards = load_data(CARDS_FILE, ["Card Name"])
    payment_options = ["Pix", "Cash"] + df_cards["Card Name"].tolist()

    # --- INPUT SECTION ---
    st.subheader("📝 New Entry")
    col1, col2, col3, col4 = st.columns(4)  # Added a 4th column for Installments!

    with col1:
        date = st.date_input("Date")
        item = st.text_input("Item Name")
    with col2:
        category = st.selectbox("Category", ["Food", "Transport", "Housing", "Fun", "Investments"])
        price = st.number_input("Total Price (R$)", step=0.01)
    with col3:
        payment_method = st.selectbox("Payment Method", payment_options)
    with col4:
        # THE NEW FEATURE: INSTALLMENTS
        installments = st.number_input("Installments", min_value=1, max_value=24, value=1, step=1)

    # --- SAVE LOGIC ---
    if st.button("Generate & Save"):
        if price > 0 and item:
            # Call the Time Machine Function
            new_df = generate_installments(date, item, price, category, payment_method, installments)

            # Save to CSV
            if os.path.exists(FINANCE_FILE):
                new_df.to_csv(FINANCE_FILE, mode='a', header=False, index=False)
            else:
                new_df.to_csv(FINANCE_FILE, index=False)

            st.success(f"✅ Generated {installments} installments for '{item}'!")
            st.rerun()
        else:
            st.error("Please enter an Item and Price.")

    st.divider()

    # --- HISTORY & FORECAST SECTION ---
    if os.path.exists(FINANCE_FILE):
        df = pd.read_csv(FINANCE_FILE)

        # 1. CONVERT TO DATE OBJECTS (Crucial for sorting)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by="Date", ascending=False)

        # 2. CREATE A "MONTH-YEAR" COLUMN (e.g., "2024-03")
        # This allows us to group expenses by month
        df["Month"] = df["Date"].dt.to_period("M").astype(str)

        st.subheader("🔮 Cash Flow Forecast")

        # 3. GROUP BY MONTH (The Analysis)
        # We sum all prices for each month
        monthly_expenses = df.groupby("Month")["Price"].sum().reset_index()

        # 4. THE FORECAST CHART
        # A Bar Chart showing how much you owe in future months
        fig = px.bar(
            monthly_expenses,
            x="Month",
            y="Price",
            title="Monthly Spending (Past & Future)",
            text_auto='.2s'  # Shows the number on top of the bar
        )
        st.plotly_chart(fig, use_container_width=True)

        # 5. THE DETAILED TABLE
        st.divider()
        st.subheader("📝 Transaction Log")
        st.dataframe(df, use_container_width=True)