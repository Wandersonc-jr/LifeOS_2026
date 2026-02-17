import streamlit as st
import pandas as pd
import os
import plotly.express as px

# --- CONFIGURATION ---
FILE_NAME = "finance.csv"
st.set_page_config(page_title="My Financial Core", page_icon="💰")

st.title("My Financial Core 💰")

# --- INPUT SECTION ---
st.subheader("📝 New Entry")
col1, col2 = st.columns(2)

with col1:
    date = st.date_input("Date")
    item = st.text_input("Item Name")
    payment_method = st.selectbox("Select Payment Method", ["Pix", "Credit Card", "Cash"])

with col2:
    category = st.selectbox("Category", ["Food", "Transport", "Housing", "Fun", "Investments"])
    price = st.number_input("Price (R$)", step=0.01)

# --- SAVE BUTTON ---
if st.button("Save Expense"):
    new_data = pd.DataFrame({
        "Date": [date],
        "Category": [category],
        "Item": [item],
        "Price": [price],
        "Payment Method": [payment_method]
    })

    if not os.path.exists(FILE_NAME):
        new_data.to_csv(FILE_NAME, index=False)
    else:
        new_data.to_csv(FILE_NAME, mode='a', header=False, index=False)

    st.success("✅ Saved successfully!")
    st.rerun()

st.divider()

# --- HISTORY & ANALYTICS SECTION ---
st.subheader("📊 History & Analytics")

# Check if file exists AND is not empty
if os.path.exists(FILE_NAME) and os.path.getsize(FILE_NAME) > 0:

    # 1. LOAD DATA
    df = pd.read_csv(FILE_NAME)

    # 2. SIDEBAR FILTERS
    st.sidebar.header("Filter Options")
    all_categories = ["All"] + df["Category"].unique().tolist()
    selected_category = st.sidebar.selectbox("Filter by Category", all_categories)

    # 3. FILTER LOGIC
    if selected_category == "All":
        filtered_df = df
    else:
        filtered_df = df[df["Category"] == selected_category]

    # 4. EDITABLE TABLE (The "Excel" Mode)
    # We allow adding/deleting rows directly in the table
    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        num_rows="dynamic",
        key="editor"
    )

    # 5. SAVE CHANGES BUTTON (With Safety Lock 🔒)
    # Only show this button if there is data to save
    if st.button("💾 Update CSV with Changes"):
        if selected_category != "All":
            st.error("⚠️ SAFETY LOCK: Please switch filter to 'All' before saving changes.")
        else:
            edited_df.to_csv(FILE_NAME, index=False)
            st.success("✅ Database Updated!")
            st.rerun()

    # 6. METRICS & CHARTS
    # We use 'edited_df' so the numbers update immediately when you edit the table
    col_metric, col_chart = st.columns([1, 2])

    with col_metric:
        total_value = edited_df["Price"].sum()
        st.metric("Total Spent", f"R$ {total_value:.2f}")

    with col_chart:
        if not edited_df.empty:
            summary = edited_df.groupby("Category")["Price"].sum().reset_index()
            fig = px.pie(summary, values="Price", names="Category", title="Expenses Breakdown", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No expenses found. Add your first item above! 👆")