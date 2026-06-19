import streamlit as st

from Pages.login import show_login_page
from Pages.theme import apply_streamlit_theme
from components.sidebar import render_app_sidebar
from components.session_state import ensure_session_state

def resetar_tela_usuario():
    
    estados = [
        "area_cliente_selecionado",
        "area_selecionada",
        "equip_cliente_selecionado",
        "equip_selecionada",
        "linha_cliente_selecionado",
        "linha_selecionada",
        "processo_cliente_selecionado",
        "processo_selecionado",
        "produto_cliente_selecionado",
        "produto_selecionado",
        "menu_grupo",
        "pagina",
    ]

    for estado in estados:
        st.session_state.pop(estado, None)

st.set_page_config(
    layout="wide",
    page_title="FBJ Pharma",
    initial_sidebar_state="expanded",
)


apply_streamlit_theme()

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNavLinkContainer"],
    [data-testid="stSidebarNavLink"],
    [data-testid="stSidebarNavLink"] *,
    [data-testid="stSidebarNavItems"] li {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

ensure_session_state({"authenticated": False, "pagina_inicial": False})

show_login_page()

if not st.session_state.get("authenticated", False):
    st.stop()

  

if not st.session_state.pagina_inicial:
    st.session_state.pagina_inicial = True
    st.switch_page("Pages/homepage.py")

render_app_sidebar()




    