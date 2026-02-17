import streamlit as st
import pandas as pd
import os
import plotly.express as px

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


# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["📊 Dashboard", "💳 Manage Cards"])

# ==============================================================================
# PAGE 1: MANAGE CARDS (The Configuration Engine)
# ==============================================================================
if page == "💳 Manage Cards":
    st.title("💳 Manage Credit Cards")
    st.info("Add your credit cards here. The Dashboard will use these rules to calculate due dates.")

    # 1. INPUT FORM
    with st.form("add_card_form"):
        col1, col2, col3 = st.columns(3)
        name = col1.text_input("Card Name (e.g., Nubank)")
        closing_day = col2.number_input("Closing Day (Melhor Dia)", min_value=1, max_value=31)
        due_day = col3.number_input("Due Day (Vencimento)", min_value=1, max_value=31)

        submitted = st.form_submit_button("Save Card")

    # 2. SAVE LOGIC
    if submitted:
        if name:
            df_cards = load_data(CARDS_FILE, ["Card Name", "Closing Day", "Due Day"])

            # Check if card already exists to avoid duplicates
            if name in df_cards["Card Name"].values:
                st.error(f"Card '{name}' already exists!")
            else:
                new_card = pd.DataFrame({
                    "Card Name": [name],
                    "Closing Day": [closing_day],
                    "Due Day": [due_day]
                })
                # Append and Save
                df_combined = pd.concat([df_cards, new_card], ignore_index=True)
                save_data(df_combined, CARDS_FILE)
                st.success(f"Card '{name}' added successfully!")
                st.rerun()
        else:
            st.warning("Please enter a Card Name.")

    # 3. DISPLAY CARDS
    st.divider()
    st.subheader("My Cards")
    df_cards = load_data(CARDS_FILE, ["Card Name", "Closing Day", "Due Day"])

    if not df_cards.empty:
        # Editable table to fix mistakes
        edited_cards = st.data_editor(df_cards, num_rows="dynamic", key="card_editor")

        if st.button("💾 Update Cards"):
            save_data(edited_cards, CARDS_FILE)
            st.success("Card list updated!")
            st.rerun()
    else:
        st.info("No cards configured yet.")

# ==============================================================================
# PAGE 2: DASHBOARD (The Transaction Logger)
# ==============================================================================
elif page == "📊 Dashboard":
    st.title("My Financial Core 💰")

    # --- LOAD CARDS FOR DROPDOWN ---
    # We read the cards file to get the names for the dropdown
    df_cards = load_data(CARDS_FILE, ["Card Name"])
    card_options = df_cards["Card Name"].tolist()

    # Merge "Standard" methods with "My Cards"
    payment_options = ["Pix", "Cash", "Debit"] + card_options

    # --- INPUT SECTION ---
    st.subheader("📝 New Entry")
    col1, col2, col3 = st.columns(3)

    with col1:
        date = st.date_input("Date")
        item = st.text_input("Item Name")

    with col2:
        category = st.selectbox("Category", ["Food", "Transport", "Housing", "Fun", "Investments"])
        price = st.number_input("Price (R$)", step=0.01)

    with col3:
        # HERE IS THE MAGIC: The list updates automatically!
        payment_method = st.selectbox("Payment Method", payment_options)

    # --- SAVE BUTTON ---
    if st.button("Save Expense"):
        new_data = pd.DataFrame({
            "Date": [date],
            "Category": [category],
            "Item": [item],
            "Price": [price],
            "Payment Method": [payment_method]
        })

        # Load existing file or create new
        if os.path.exists(FINANCE_FILE):
            new_data.to_csv(FINANCE_FILE, mode='a', header=False, index=False)
        else:
            new_data.to_csv(FINANCE_FILE, index=False)

        st.success("✅ Saved successfully!")
        st.rerun()

    st.divider()

    # --- HISTORY SECTION ---
    st.subheader("📊 History")

    if os.path.exists(FINANCE_FILE) and os.path.getsize(FINANCE_FILE) > 0:
        df = pd.read_csv(FINANCE_FILE)

        # Sidebar Filter
        st.sidebar.header("Filter Dashboard")
        all_cats = ["All"] + df["Category"].unique().tolist()
        sel_cat = st.sidebar.selectbox("Category", all_cats)

        if sel_cat != "All":
            df = df[df["Category"] == sel_cat]

        # Editable Table
        edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="dash_editor")

        if st.button("💾 Update History"):
            if sel_cat != "All":
                st.error("⚠️ Switch filter to 'All' before saving.")
            else:
                edited_df.to_csv(FINANCE_FILE, index=False)
                st.success("Updated!")
                st.rerun()

        # Metrics
        total = edited_df["Price"].sum()
        st.metric("Total Spent", f"R$ {total:.2f}")

    else:
        st.info("No expenses yet.")