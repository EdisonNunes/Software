import streamlit as st
from components.top_menu import render_top_menu
from components.sidebar import render_app_sidebar

if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

render_app_sidebar()

st.markdown(
    """
    <style>
    .st-key-home_menu_direita {
        position: sticky;
        top: 0.75rem;
        z-index: 100;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container(key="home_menu_direita"):
    render_top_menu()
