import streamlit as st


def render_top_menu():

    # =====================================================
    # MENU PRINCIPAL
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button(
            "🏠 Home",
            use_container_width=True,
            key="tm_top_home"
        ):
            st.switch_page("Pages/homepage.py")

    with c2:
        if st.button(
            "📋 Planejamento",
            use_container_width=True,
            key="tm_top_planejamento"
        ):
            st.session_state.menu_grupo = "planejamento"
            st.rerun()

    with c3:
        if st.button(
            "🏭 Cadastros",
            use_container_width=True,
            key="tm_top_cadastros"
        ):
            st.session_state.menu_grupo = "cadastros"
            st.rerun()

    with c4:
        if st.button(
            "⚙️ Configurações",
            use_container_width=True,
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
                use_container_width=True,
                key="tm_sub_demanda"
            ):
                st.switch_page("Pages/demandas.py")

        with c2:
            if st.button(
                "📅 Paradas",
                use_container_width=True,
                key="tm_sub_paradas"
            ):
                st.switch_page("Pages/paradas.py")

    # =====================================================
    # SUBMENU CADASTROS
    # =====================================================

    elif st.session_state.get("menu_grupo") == "cadastros":

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            if st.button(
                "🏭 Áreas",
                use_container_width=True,
                key="tm_sub_areas"
            ):
                st.switch_page("Pages/areas.py")

        with c2:
            if st.button(
                "🏗️ Linhas",
                use_container_width=True,
                key="tm_sub_linhas"
            ):
                st.switch_page("Pages/linhas.py")

        with c3:
            if st.button(
                "⚙️ Processos",
                use_container_width=True,
                key="tm_sub_processos"
            ):
                st.switch_page("Pages/processos.py")

        with c4:
            if st.button(
                "🔧 Equipamentos",
                use_container_width=True,
                key="tm_sub_equipamentos"
            ):
                st.switch_page("Pages/equipamentos.py")

        with c5:
            if st.button(
                "📦 Produtos",
                use_container_width=True,
                key="tm_sub_produtos"
            ):
                st.switch_page("Pages/produtos.py")

    # =====================================================
    # SUBMENU CONFIGURAÇÕES
    # =====================================================

    elif st.session_state.get("menu_grupo") == "configuracoes":

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            if st.button(
                "📦 SKU",
                use_container_width=True,
                key="tm_sub_sku"
            ):
                st.switch_page("Pages/produtos.py")

        with c2:
            if st.button(
                "🎨 Layout",
                use_container_width=True,
                key="tm_sub_layout"
            ):
                st.switch_page("Pages/layout.py")

        # Apenas Admin/Supervisor
        if st.session_state.get("role") in ["admin", "supervisor"]:

            with c3:
                if st.button(
                    "🏢 Clientes",
                    use_container_width=True,
                    key="tm_sub_clientes"
                ):
                    st.switch_page("Pages/clientes.py")

            with c4:
                if st.button(
                    "👥 Usuários",
                    use_container_width=True,
                    key="tm_sub_usuarios"
                ):
                    st.switch_page("Pages/usuarios.py")

    st.divider()