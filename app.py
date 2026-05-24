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
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "current_user_display_name" not in st.session_state:
    st.session_state["current_user_display_name"] = None
if "session_id" not in st.session_state:
    import uuid

    st.session_state["session_id"] = str(uuid.uuid4())

# Roteamento
if not st.session_state["logged_in"]:
    from src.pages.login import render as render_login

    render_login()
else:
    from src.pages.dashboard import render as render_dashboard

    render_dashboard()
