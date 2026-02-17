import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from dateutil.relativedelta import relativedelta
from datetime import date as dt_class

# --- CONFIGURATION ---
st.set_page_config(page_title="My Financial Core (SQL)", page_icon="🏦", layout="wide")
DB_NAME = "finance.db"


# --- DATABASE ENGINE ---
def get_connection():
    return sqlite3.connect(DB_NAME)


def load_data(table_name):
    """Reads a SQL table into a Pandas DataFrame."""
    conn = get_connection()
    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error loading {table_name}: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def run_query(query, params=()):
    """Executes a SQL command (INSERT, UPDATE, DELETE)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        st.error(f"Database Error: {e}")
    finally:
        conn.close()


# --- LOGIC ENGINE (Updated for SQL) ---
def generate_installments(date, item, price, category, payment_method, installments):
    new_rows = []

    # Load Card Rules (SQL Version)
    cards_df = load_data("cards")
    # Note: Our migration script renamed columns to lowercase: card_name, closing_day, due_day
    card_rule = cards_df[cards_df["card_name"] == payment_method]
    is_credit_card = not card_rule.empty

    for i in range(installments):
        if is_credit_card:
            closing_day = int(card_rule.iloc[0]["closing_day"])
            due_day = int(card_rule.iloc[0]["due_day"])

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

        # We store rows as tuples for SQL insertion
        new_rows.append((row_date, category, item_name, item_price, payment_method))

    return new_rows


# --- SIDEBAR NAVIGATION ---
page = st.sidebar.radio("Go to", [
    "📊 Dashboard",
    "💸 Expenses (Entry)",
    "💰 Incomes (Entry)",
    "🎯 Set Budgets", # <--- Add this
    "💳 Manage Cards"
])

# ==============================================================================
# PAGE 1: DASHBOARD (SQL ANALYTICS)
# ==============================================================================
if page == "📊 Dashboard":
    st.title("📊 Executive Dashboard (SQL)")

    # 1. LOAD DATA
    df_expenses = load_data("expenses")
    df_income = load_data("incomes")

    # Handle Dates
    if not df_expenses.empty:
        df_expenses["Date"] = pd.to_datetime(df_expenses["Date"])
    if not df_income.empty:
        df_income["Date"] = pd.to_datetime(df_income["Date"])

    # --- START OF DATA CHECK ---
    if not df_expenses.empty or not df_income.empty:
        current_month = dt_class.today().strftime("%Y-%m")

        # Calculate Metrics
        total_expenses = 0.0
        if not df_expenses.empty:
            df_expenses["Month"] = df_expenses["Date"].dt.to_period("M").astype(str)
            total_expenses = df_expenses[df_expenses["Month"] == current_month]["Price"].sum()

        total_income = 0.0
        if not df_income.empty:
            df_income["Month"] = df_income["Date"].dt.to_period("M").astype(str)
            total_income = df_income[df_income["Month"] == current_month]["Price"].sum()

        savings = total_income - total_expenses

        # Display Metrics (Top Row)
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Income", f"R$ {total_income:,.2f}")
        c2.metric("💸 Expenses", f"R$ {total_expenses:,.2f}", delta_color="inverse")
        c3.metric("🐷 Savings", f"R$ {savings:,.2f}", delta=f"{savings:,.2f}")

        st.divider()

        # --- TOP CHARTS (Two Columns) ---
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("Cash Flow")
            combined = pd.DataFrame()
            if not df_expenses.empty:
                e = df_expenses.groupby("Month")["Price"].sum().reset_index()
                e["Type"] = "Expense"
                combined = pd.concat([combined, e])
            if not df_income.empty:
                i = df_income.groupby("Month")["Price"].sum().reset_index()
                i["Type"] = "Income"
                combined = pd.concat([combined, i])

            if not combined.empty:
                fig = px.bar(combined, x="Month", y="Price", color="Type", barmode="group")
                st.plotly_chart(fig, use_container_width=True)

        with col_chart2:
            st.subheader("Category Breakdown")
            if not df_expenses.empty:
                cat_sum = df_expenses.groupby("Category")["Price"].sum().reset_index()
                fig = px.pie(cat_sum, values="Price", names="Category", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)

        # --- BUDGET TRACKER (Full Width - Outside the columns!) ---
        st.divider()
        st.subheader("🎯 Monthly Budget Tracker")

        budget_settings = load_data("budgets")

        conn_budget = get_connection()
        spent_df = pd.read_sql("""
                                 SELECT Category, SUM(Price) as Spent
                                 FROM expenses
                                 WHERE strftime('%Y-%m', Date) = strftime('%Y-%m', 'now')
                                 GROUP BY Category
                                  """, conn_budget)
        conn_budget.close()

        if not budget_settings.empty:
             for _, row in budget_settings.iterrows():
                cat = str(row['category']).strip()
                limit = row['amount']

                spent_row = spent_df[spent_df['Category'] == cat]
                spent = float(spent_row['Spent'].iloc[0]) if not spent_row.empty else 0.0

                if limit > 0:
                    col_text, col_bar = st.columns([1, 2])
                    with col_text:
                        st.markdown(f"**{cat}**")
                        st.caption(f"R$ {spent:,.2f} / R$ {limit:,.2f}")
                    with col_bar:
                        percent = min(spent / limit, 1.0)
                        st.progress(percent)
                        if spent > limit:
                            st.caption(f"⚠️ Over by R$ {spent - limit:,.2f}")
        else:
            st.warning("No budgets found. Go to 'Set Budgets' to configure them.")

        # --- DEEP INSIGHTS (Full Width) ---
        st.divider()
        st.subheader("🕵️‍♂️ Deep Insights")

        conn = get_connection()

        # 1. Categories Query
        query = """
                   SELECT Category,
                         'R$ ' || printf('%.2f', SUM(Price)) as Total,
                        COUNT(*)                            as Transactions,
                        'R$ ' || printf('%.2f', AVG(Price)) as Average
                   FROM expenses
                   GROUP BY Category
                  ORDER BY SUM(Price) DESC
                  """
        stats_df = pd.read_sql(query, conn)
        st.table(stats_df)

        # 2. Weekday Query
        st.subheader("📅 Spending by Day of Week")
        weekday_query = """
                        SELECT CASE CAST(strftime('%w', Date) AS INT)
                                      WHEN 0 THEN 'Sunday'
                                      WHEN 1 THEN 'Monday'
                                      WHEN 2 THEN 'Tuesday'
                                      WHEN 3 THEN 'Wednesday'
                                      WHEN 4 THEN 'Thursday'
                                      WHEN 5 THEN 'Friday'
                                      WHEN 6 THEN 'Saturday'
                                   END    as Weekday,
                               SUM(Price) as Total
                           FROM expenses
                          GROUP BY Weekday
                          ORDER BY Total DESC
                          """
        weekday_df = pd.read_sql(weekday_query, conn)
        st.plotly_chart(px.bar(weekday_df, x='Weekday', y='Total'), use_container_width=True)

        # 3. Whale Query
        whale_query = "SELECT Date, Item, Category, Price FROM expenses ORDER BY Price DESC LIMIT 1"
        whale_df = pd.read_sql(whale_query, conn)

        if not whale_df.empty:
            st.warning(f"Your biggest single purchase: **{whale_df.iloc[0]['Item']}** (R$ {whale_df.iloc[0]['Price']:,.2f})")

        conn.close()

    else:
        st.info("Database is empty. Add data!")


# ==============================================================================
# PAGE 2: EXPENSES (SQL INSERT)
# ==============================================================================
elif page == "💸 Expenses (Entry)":
    st.title("💸 Expenses (SQL)")

    # Load Card Names for Dropdown
    df_cards = load_data("cards")
    # Safe handling if table is empty
    card_list = df_cards["card_name"].tolist() if not df_cards.empty else []
    payment_options = ["Pix", "Cash"] + card_list

    with st.form("expense_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        date = c1.date_input("Date")
        item = c1.text_input("Item")
        category = c2.selectbox("Category", ["Food", "Transport", "Housing", "Fun", "Investments"])
        price = c2.number_input("Price", step=0.01)
        method = c3.selectbox("Payment", payment_options)
        installments = c4.number_input("Installments", 1, 24, 1)

        if st.form_submit_button("Save to DB"):
            if price > 0 and item:
                # 1. Generate Rows
                rows_to_insert = generate_installments(date, item, price, category, method, installments)

                # 2. Insert into SQL
                conn = get_connection()
                cursor = conn.cursor()
                cursor.executemany("""
                                   INSERT INTO expenses (Date, Category, Item, Price, "Payment Method")
                                   VALUES (?, ?, ?, ?, ?)
                                   """, rows_to_insert)
                conn.commit()
                conn.close()

                st.success(f"Saved {len(rows_to_insert)} rows to Database!")
                st.rerun()

    st.divider()

    # --- DELETE SECTION (NEW!) ---
    with st.expander("🗑️ Delete a Transaction"):
        col_del1, col_del2 = st.columns([3, 1])
        delete_id = col_del1.number_input("Enter ID to delete", step=1, min_value=1)

        if col_del2.button("Delete Row"):
            conn = get_connection()
            cursor = conn.cursor()
            try:
                # 1. Check if ID exists
                cursor.execute("SELECT * FROM expenses WHERE id=?", (delete_id,))
                data = cursor.fetchone()
                if data:
                    # 2. DELETE command
                    cursor.execute("DELETE FROM expenses WHERE id=?", (delete_id,))
                    conn.commit()
                    st.success(f"Row {delete_id} deleted successfully!")
                    st.rerun()
                else:
                    st.error("ID not found.")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                conn.close()

    # --- SHOW DATA WITH ID ---
    # We now SELECT 'id' explicitly so you can see it
    conn = get_connection()
    df = pd.read_sql("SELECT id, Date, Category, Item, Price, 'Payment Method' FROM expenses ORDER BY Date DESC", conn)
    conn.close()

    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        # Move ID to the first column visually
        st.dataframe(df, use_container_width=True, hide_index=True)

# ==============================================================================
# PAGE 3: INCOMES (SQL INSERT)
# ==============================================================================
elif page == "💰 Incomes (Entry)":
    st.title("💰 Incomes (SQL)")

    with st.form("income_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        date = c1.date_input("Date")
        category = c2.selectbox("Category", ["Salary", "Freelance", "Dividends", "Other"])
        price = c3.number_input("Amount", step=0.01)
        item = st.text_input("Description")

        if st.form_submit_button("Save Income"):
            if price > 0:
                run_query("""
                          INSERT INTO incomes (Date, Category, Item, Price)
                          VALUES (?, ?, ?, ?)
                          """, (date, category, item, price))
                st.success("Income Saved to DB!")
                st.rerun()

    st.divider()
    df = load_data("incomes")
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by="Date", ascending=False)
        st.dataframe(df, use_container_width=True)

elif page == "🎯 Set Budgets":
    st.title("🎯 Monthly Budget Settings")

    categories = ["Food", "Transport", "Housing", "Fun", "Investments"]

    # Load current budgets from DB
    current_budgets = load_data("budgets")

    with st.form("budget_form"):
        new_budgets = {}
        for cat in categories:
            # Look up existing value or default to 0.0
            existing_val = current_budgets[current_budgets['category'] == cat]['amount'].values
            default_val = float(existing_val[0]) if len(existing_val) > 0 else 0.0

            new_budgets[cat] = st.number_input(f"Limit for {cat}", min_value=0.0, value=default_val, step=50.0)

        if st.form_submit_button("Update All Budgets"):
            for cat, amount in new_budgets.items():
                # SQL "REPLACE" or "INSERT OR REPLACE" is great for settings
                run_query("INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)", (cat, amount))
            st.success("Budgets updated!")
            st.rerun()

# ==============================================================================
# PAGE 4: CARDS (SQL INSERT)
# ==============================================================================
elif page == "💳 Manage Cards":
    st.title("💳 Manage Cards (SQL)")

    with st.form("card_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Card Name")
        closing = c2.number_input("Closing Day", 1, 31)
        due = c3.number_input("Due Day", 1, 31)

        if st.form_submit_button("Save Card"):
            if name:
                try:
                    run_query("""
                              INSERT INTO cards (card_name, closing_day, due_day)
                              VALUES (?, ?, ?)
                              """, (name, closing, due))
                    st.success("Card Saved!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error (Card might exist): {e}")

    st.divider()
    df = load_data("cards")
    st.dataframe(df, use_container_width=True)

