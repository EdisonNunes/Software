import streamlit as st

from components.sidebar import render_app_sidebar
from components.top_menu import render_top_menu


if not st.session_state.get("authenticated", False):
	st.switch_page("main.py")

render_app_sidebar()
render_top_menu()

st.info("# Demandas", icon=":material/view_timeline:")
st.caption("Pagina em construcao.")
