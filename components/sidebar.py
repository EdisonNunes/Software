import streamlit as st
from pathlib import Path

from pages.crud import supabase


def _logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.clear()
    st.switch_page("main.py")


def _render_sidebar_logo():
    logo_candidates = [
        Path("imagens/logo1.png"),
        Path("Imagens/Logo1.png"),
        Path("Imagens/logo1.png"),
        Path("imagens/Logo1.png"),
    ]

    logo_path = next((str(path) for path in logo_candidates if path.exists()), None)
    if not logo_path:
        return

    try:
        st.image(logo_path, width='stretch')
    except TypeError:
        # Compatibilidade com versões antigas do Streamlit.
        st.image(logo_path, width=220)
    except Exception:
        # Não interrompe a renderização da página caso haja falha no logo.
        pass


def render_app_sidebar():
    with st.sidebar:
        _render_sidebar_logo()
        st.divider()

        st.caption(f"👤 {st.session_state.get('user_name', '')}")

        if st.session_state.get("empresa"):
            st.caption(f"🏢 {st.session_state.get('empresa')}")

        st.caption(f"🔑 {st.session_state.get('role', '').upper()}")
        st.caption("Versão: 2.0")

        st.divider()

        if st.button("🚪 Logout", use_container_width=True, key="sb_logout"):
            _logout()

