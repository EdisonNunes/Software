import streamlit as st

from pages.crud import supabase


def _logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.clear()
    st.switch_page("main.py")


def render_app_sidebar():
    with st.sidebar:
        st.title("?? FBJ Pharma", text_alignment='center')
        st.caption("Sistema de Planejamento e Gestão Industrial", text_alignment='center')
        st.divider()

        st.caption(f"?? {st.session_state.get('user_name', '')}")

        if st.session_state.get("empresa"):
            st.caption(f"?? {st.session_state.get('empresa')}")

        st.caption(f"?? {st.session_state.get('role', '').upper()}")
        st.caption("Versão: 3.0")

        st.divider()

        if st.button("?? Logout", width='stretch', key="sb_logout"):
            _logout()

