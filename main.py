import streamlit as st

from pages.login import show_login_page
from pages.theme import apply_streamlit_theme
from components.sidebar import render_app_sidebar
from components.session_state import ensure_session_state
from core.database import get_supabase_client

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

ensure_session_state({"authenticated": False, "pagina_inicial": False, "acesso_suspenso": False})

show_login_page()

if not st.session_state.get("authenticated", False):
    st.stop()

if st.session_state.get("acesso_suspenso", False):
    st.markdown(
        """
        <style>
        .suspended-overlay {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
        }
        .suspended-card {
            background: linear-gradient(135deg, #1E1E2E 0%, #2D1B1B 100%);
            border: 2px solid #DC2626;
            border-radius: 20px;
            padding: 60px 80px;
            text-align: center;
            box-shadow: 0 0 40px rgba(220, 38, 38, 0.35);
            max-width: 560px;
        }
        .suspended-icon {
            font-size: 72px;
            margin-bottom: 16px;
        }
        .suspended-title {
            font-size: 32px;
            font-weight: 800;
            color: #FCA5A5;
            margin-bottom: 12px;
            letter-spacing: 1px;
        }
        .suspended-msg {
            font-size: 18px;
            color: #E2E8F0;
            margin-bottom: 8px;
        }
        .suspended-contact {
            font-size: 20px;
            font-weight: 700;
            color: #F97316;
            margin-top: 10px;
        }
        </style>
        <div class="suspended-overlay">
          <div class="suspended-card">
            <div class="suspended-icon">\U0001f6ab</div>
            <div class="suspended-title">Acesso Suspenso</div>
            <div class="suspended-msg">Seu acesso ao sistema foi temporariamente suspenso.</div>
            <div class="suspended-contact">Entre em contato com<br>FBJ Pharma</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    col_c, col_btn, col_d = st.columns([2, 1, 2])
    with col_btn:
        if st.button("OK", use_container_width=True, type="primary"):
            supabase_logout = get_supabase_client()
            try:
                supabase_logout.auth.sign_out()
            except Exception:
                pass
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    st.stop()

if not st.session_state.pagina_inicial:
    st.session_state.pagina_inicial = True
    st.switch_page("pages/homepage.py")

render_app_sidebar()




    
