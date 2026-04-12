"""
app.py — Ponto de entrada do Ask My Data.
Roteia entre a tela de Login e o Dashboard usando session_state.
"""
import streamlit as st

st.set_page_config(
    page_title="Ask My Data",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="auto",
)

# Inicializar estado
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Roteamento
if not st.session_state["logged_in"]:
    from src.pages.login import render as render_login
    render_login()
else:
    from src.pages.dashboard import render as render_dashboard
    render_dashboard()
