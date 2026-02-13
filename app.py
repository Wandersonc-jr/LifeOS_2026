import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# ==================== CONFIG ====================
st.set_page_config(
    page_title="Finances & Ops",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== CSS STYLING (MODERN FINTECH) ====================
def local_css():
    st.markdown("""
    <style>
    /* Import Clean Font (Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* Global Settings */
    .stApp {
        background-color: #0E1117; /* GitHub Dark Mode Background */
        color: #E6EDF3;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar - Clean & Subtle */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }

    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700;
        color: #FFFFFF !important;
        letter-spacing: -0.5px;
    }

    h1 { font-size: 2.5rem !important; }
    h2 { font-size: 1.8rem !important; border-bottom: 1px solid #30363D; padding-bottom: 10px; }
    h3 { font-size: 1.2rem !important; color: #8B949E !important; }

    /* Modern Card (The "Fintech" Container) */
    .fintech-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }

    .fintech-card:hover {
        border-color: #58A6FF; /* Subtle Blue Hover */
    }

    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif;
        font-size: 36px !important;
        font-weight: 700;
        color: #FFFFFF !important;
    }

    [data-testid="stMetricLabel"] {
        color: #8B949E !important;
        font-size: 14px !important;
        font-weight: 500;
        text-transform: uppercase;
    }

    /* Buttons - Professional Blue */
    .stButton > button {
        background-color: #238636; /* Success Green */
        color: white;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        border: 1px solid rgba(240, 246, 252, 0.1);
        border-radius: 6px;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background-color: #2EA043;
        border-color: #8B949E;
        transform: scale(1.02);
    }

    /* Input Fields - Dark & Clean */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input {
        background-color: #0D1117 !important;
        color: #E6EDF3 !important;
        border: 1px solid #30363D !important;
        border-radius: 6px;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #58A6FF !important;
    }

    /* Dataframe - Professional Table */
    .dataframe {
        background-color: #161B22 !important;
        color: #E6EDF3 !important;
        border: 1px solid #30363D;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #238636;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-weight: 600;
        font-size: 16px;
    }

    /* Remove default top padding */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ==================== DATA SETUP ====================
DATA_FOLDER = "data"
FINANCE_FILE = os.path.join(DATA_FOLDER, "finances.csv")

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

if not os.path.exists(FINANCE_FILE):
    df_init = pd.DataFrame(columns=["Data", "Categoria", "Descrição", "Valor", "Tipo"])
    df_init.to_csv(FINANCE_FILE, index=False)


def load_data():
    return pd.read_csv(FINANCE_FILE)


def save_transaction(date, category, desc, value, type_t):
    new_data = pd.DataFrame({
        "Data": [date],
        "Categoria": [category],
        "Descrição": [desc],
        "Valor": [value],
        "Tipo": [type_t]
    })
    new_data.to_csv(FINANCE_FILE, mode='a', header=False, index=False)


# Apply CSS
local_css()

# ==================== SIDEBAR ====================
st.sidebar.markdown('### 🧭 NAVIGATION')
menu = st.sidebar.radio("", ["Dashboard Overview", "Finance Operations", "English Training", "Project Management"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 STATUS")
st.sidebar.info(f"Date: {datetime.now().strftime('%b %d, %Y')}")

# ==================== PAGES ====================

# 1. HOME
if menu == "Dashboard Overview":
    st.markdown("<h1>Executive Summary</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8B949E;'>High-level metrics and system status.</p>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.metric("Time Remaining (2027)", "325 Days", "On Track")
        st.caption("Primary Goal: English Fluency")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.metric("Active Projects", "3", "+1 This Week")
        st.caption("Focus: Security Portfolio")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.metric("System Health", "100%", "Stable")
        st.caption("All systems operational")
        st.markdown('</div>', unsafe_allow_html=True)

# 2. FINANCE
elif menu == "Finance Operations":
    st.markdown("<h1>Financial Operations</h1>", unsafe_allow_html=True)

    # Input Form (Clean Expander)
    with st.expander("➕ New Transaction Entry", expanded=False):
        with st.form("finance_form"):
            col1, col2, col3 = st.columns(3)
            data_input = col1.date_input("Date")
            tipo_input = col2.selectbox("Type", ["Despesa", "Receita", "Investimento"])
            valor_input = col3.number_input("Amount (R$)", min_value=0.0, format="%.2f")

            c1, c2 = st.columns([2, 1])
            desc_input = c1.text_input("Description")
            cat_input = c2.selectbox("Category",
                                     ["Moradia", "Alimentação", "Lazer", "Salário", "FIIs", "Ações", "Educação"])

            submitted = st.form_submit_button("Submit Transaction")
            if submitted:
                save_transaction(data_input, cat_input, desc_input, valor_input, tipo_input)
                st.success("Transaction recorded successfully.")
                st.rerun()

    # Data Viz
    df = load_data()

    if not df.empty:
        # Metrics Row
        st.markdown("### 📊 Cash Flow Analysis")

        receitas = df[df["Tipo"] == "Receita"]["Valor"].sum()
        despesas = df[df["Tipo"] == "Despesa"]["Valor"].sum()
        investido = df[df["Tipo"] == "Investimento"]["Valor"].sum()
        saldo = receitas - despesas - investido

        m1, m2, m3, m4 = st.columns(4)


        # Helper to style metrics cleaner
        def metric_card(label, value, prefix="R$ "):
            st.markdown(f"""
            <div class="fintech-card" style="padding: 15px; text-align: center;">
                <p style="color: #8B949E; font-size: 12px; margin:0;">{label}</p>
                <h2 style="margin:0; border:none; font-size: 24px;">{prefix}{value:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)


        with m1:
            metric_card("TOTAL REVENUE", receitas)
        with m2:
            metric_card("TOTAL EXPENSES", despesas)
        with m3:
            metric_card("INVESTMENTS", investido)
        with m4:
            metric_card("NET BALANCE", saldo)

        # Charts
        c1, c2 = st.columns([1, 1])

        df_despesas = df[df["Tipo"] == "Despesa"]
        if not df_despesas.empty:
            # Clean Pie Chart
            fig_pie = px.pie(
                df_despesas,
                values='Valor',
                names='Categoria',
                color_discrete_sequence=px.colors.sequential.Teal,  # Professional Colors
                hole=0.4  # Donut chart looks more modern
            )
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#E6EDF3', family='Inter'),
                showlegend=True,
                margin=dict(t=30, b=0, l=0, r=0)
            )
            with c1:
                st.markdown('<div class="fintech-card"><h3>Expense Distribution</h3>', unsafe_allow_html=True)
                st.plotly_chart(fig_pie, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="fintech-card"><h3>Recent Activity</h3>', unsafe_allow_html=True)
            st.dataframe(df.tail(8), hide_index=True, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# 3. ENGLISH
elif menu == "English Training":
    st.markdown("<h1>English Proficiency</h1>", unsafe_allow_html=True)

    st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Progression Path")
    st.progress(60)
    st.caption("Current Level: B1 (Intermediate) — Target: C1 (Advanced)")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.markdown("### Daily Habits")
        st.checkbox("ELSA Speak (20 min)")
        st.checkbox("Shadowing MBJ (30 min)")
        st.checkbox("Anki Review (50 words)")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.markdown("### Vocabulary Capture")
        word = st.text_input("New Word", placeholder="e.g. Ubiquitous")
        if st.button("Save to Database"):
            st.toast(f"Saved: {word}")
        st.markdown('</div>', unsafe_allow_html=True)

# 4. PROJECTS
elif menu == "Project Management":
    st.markdown("<h1>Development Portfolio</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Current Sprint", "Backlog"])

    with tab1:
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.markdown("### 🛡️ Security Analyst Path")
        st.checkbox("Create Password Hash Script", value=True)
        st.checkbox("Access Log Dashboard (SQL)", value=False)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="fintech-card">', unsafe_allow_html=True)
        st.code("""
# Project Idea: Pix Fraud Detection
# Tech Stack: Pandas, Scikit-Learn
# Priority: High
        """, language="python")
        st.markdown('</div>', unsafe_allow_html=True)