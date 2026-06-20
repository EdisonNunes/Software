import streamlit as st


def render_top_menu():

    # =====================================================
    # MENU PRINCIPAL
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button(
            "🏠 Home",
            width="stretch",
            key="tm_top_home"
        ):
            st.switch_page("pages/homepage.py")

    with c2:
        if st.button(
            "📋 Planejamento",
            width="stretch",
            key="tm_top_planejamento"
        ):
            st.session_state.menu_grupo = "planejamento"
            st.rerun()

    with c3:
        if st.button(
            "🏭 Cadastros",
            width="stretch",
            key="tm_top_cadastros"
        ):
            st.session_state.menu_grupo = "cadastros"
            st.rerun()

    with c4:
        if st.button(
            "⚙️ Configurações",
            width="stretch",
            key="tm_top_config"
        ):
            st.session_state.menu_grupo = "configuracoes"
            st.rerun()

    st.divider()

    # =====================================================
    # SUBMENU PLANEJAMENTO
    # =====================================================

    if st.session_state.get("menu_grupo") == "planejamento":

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            if st.button(
                "📈 Demandas",
                width="stretch",
                key="tm_sub_demanda"
            ):
                st.switch_page("pages/demandas.py")

        with c2:
            if st.button(
                "📅 Paradas",
                width="stretch",
                key="tm_sub_paradas"
            ):
                st.switch_page("pages/paradas.py")

    # =====================================================
    # SUBMENU CADASTROS
    # =====================================================

    elif st.session_state.get("menu_grupo") == "cadastros":

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            if st.button(
                "🏭 Áreas",
                width="stretch",
                key="tm_sub_areas"
            ):
                st.switch_page("pages/areas.py")

        with c2:
            if st.button(
                "🏗️ Linhas",
                width="stretch",
                key="tm_sub_linhas"
            ):
                st.switch_page("pages/linhas.py")

        with c3:
            if st.button(
                "⚙️ Processos",
                width="stretch",
                key="tm_sub_processos"
            ):
                st.switch_page("pages/processos.py")

        with c4:
            if st.button(
                "🔧 Equipamentos",
                width="stretch",
                key="tm_sub_equipamentos"
            ):
                st.switch_page("pages/equipamentos.py")

        with c5:
            if st.button(
                "📦 Produtos",
                width="stretch",
                key="tm_sub_produtos"
            ):
                st.switch_page("pages/produtos.py")

    # =====================================================
    # SUBMENU CONFIGURAÇÕES
    # =====================================================

    elif st.session_state.get("menu_grupo") == "configuracoes":

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            if st.button(
                "📦 SKU",
                width="stretch",
                key="tm_sub_sku"
            ):
                st.switch_page("pages/produtos.py")

        with c2:
            if st.button(
                "🎨 Layout",
                width="stretch",
                key="tm_sub_layout"
            ):
                st.switch_page("pages/layout.py")

        # Apenas Admin/Supervisor
        if st.session_state.get("role") in ["admin", "supervisor"]:

            with c3:
                if st.button(
                    "🏢 Clientes",
                    width="stretch",
                    key="tm_sub_clientes"
                ):
                    st.switch_page("pages/clientes.py")

            with c4:
                if st.button(
                    "👥 Usuários",
                    width="stretch",
                    key="tm_sub_usuarios"
                ):
                    st.switch_page("pages/usuarios.py")

    st.divider()

