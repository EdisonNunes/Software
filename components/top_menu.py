import streamlit as st


def render_top_menu():
    if "menu_grupo" not in st.session_state:
        st.session_state.menu_grupo = None

    if "menu_submenu_visivel" not in st.session_state:
        st.session_state.menu_submenu_visivel = False

    if "menu_item_selecionado" not in st.session_state:
        st.session_state.menu_item_selecionado = ""

    def _botao_pagina(coluna, rotulo, key, pagina, submenu=False):
        with coluna:
            if st.button(rotulo, width='stretch', key=key):
                if submenu:
                    st.session_state.menu_item_selecionado = rotulo
                    st.session_state.menu_submenu_visivel = False
                else:
                    st.session_state.menu_item_selecionado = ""
                    st.session_state.menu_submenu_visivel = False
                st.switch_page(pagina)

    def _botao_grupo(coluna, rotulo, key, grupo):
        with coluna:
            if st.button(rotulo, width='stretch', key=key):
                # Ao trocar de grupo, limpa o item anterior para evitar conteúdo residual.
                st.session_state.menu_item_selecionado = ""

                if st.session_state.menu_grupo == grupo and st.session_state.menu_submenu_visivel:
                    st.session_state.menu_submenu_visivel = False
                else:
                    st.session_state.menu_grupo = grupo
                    st.session_state.menu_submenu_visivel = True
                st.switch_page("pages/homepage.py")

    # =====================================================
    # MENU PRINCIPAL
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    _botao_pagina(c1, "\U0001F3E0 Home", "tm_top_home", "pages/homepage.py")
    _botao_grupo(c2, "\U0001F4CB Planejamento", "tm_top_planejamento", "planejamento")
    _botao_grupo(c3, "\U0001F3ED Cadastros", "tm_top_cadastros", "cadastros")
    _botao_grupo(c4, "\U0001F9ED Administração", "tm_top_adm", "administracao")

    st.divider()

    if st.session_state.get("menu_item_selecionado"):
        st.caption(f"Selecionado: {st.session_state.get('menu_item_selecionado')}")

    # =====================================================
    # SUBMENU PLANEJAMENTO
    # =====================================================

    if not st.session_state.get("menu_submenu_visivel", False):
        return

    if st.session_state.get("menu_grupo") == "planejamento":

        c1, c2, c3, c4 = st.columns(4)
        _botao_pagina(c1, "\U0001F9E0 Planejamento MES", "tm_sub_planejamento_mes", "pages/planejamento.py", submenu=True)
        _botao_pagina(c2, "\U0001F4C8 Demandas", "tm_sub_demanda", "pages/demandas.py", submenu=True)
        _botao_pagina(c3, "\U0001F4C5 Paradas", "tm_sub_paradas", "pages/paradas.py", submenu=True)
        _botao_pagina(c4, "\U0001F3AF Metas", "tm_sub_metas", "pages/metas.py", submenu=True)

    # =====================================================
    # SUBMENU CADASTROS
    # =====================================================

    elif st.session_state.get("menu_grupo") == "cadastros":
        st.caption("Operacionais")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        _botao_pagina(c1, "\U0001F3ED Áreas", "tm_sub_areas", "pages/areas.py", submenu=True)
        _botao_pagina(c2, "\U0001F3D7\uFE0F Linhas", "tm_sub_linhas", "pages/linhas.py", submenu=True)
        _botao_pagina(c3, "\u2699\uFE0F Processos", "tm_sub_processos", "pages/processos.py", submenu=True)
        _botao_pagina(c4, "\U0001F527 Equipamentos", "tm_sub_equipamentos", "pages/equipamentos.py", submenu=True)
        _botao_pagina(c5, "\u23F1\uFE0F Turnos", "tm_sub_turnos", "pages/turnos.py", submenu=True)
        _botao_pagina(c6, "\U0001F4E6 SKU", "tm_sub_produtos", "pages/produtos.py", submenu=True)

        st.caption("Auxiliares")
        c7, c8, c9, c10 = st.columns(4)
        _botao_pagina(c7, "\U0001F9E9 Famílias", "tm_sub_familias", "pages/familias_produtos.py", submenu=True)
        _botao_pagina(c8, "\U0001F4D0 Unidades", "tm_sub_unidades", "pages/unidades.py", submenu=True)
        _botao_pagina(c9, "\U0001FAAA Cargos", "tm_sub_cargos", "pages/cargos.py", submenu=True)
        _botao_pagina(c10, "\U0001F4C5 Paradas", "tm_sub_paradas_cad", "pages/paradas.py", submenu=True)

    # =====================================================
    # SUBMENU ADMINISTRAÇÃO
    # =====================================================

    elif st.session_state.get("menu_grupo") in ["administracao", "configuracoes"]:
        c1, c2, c3 = st.columns(3)
        _botao_pagina(c1, "\U0001F3A8 Layout", "tm_sub_layout", "pages/layout.py", submenu=True)

        # Apenas Admin/Supervisor
        if st.session_state.get("role") in ["admin", "supervisor"]:
            _botao_pagina(c2, "\U0001F3E2 Clientes", "tm_sub_clientes", "pages/clientes.py", submenu=True)
            _botao_pagina(c3, "\U0001F465 Usuários", "tm_sub_usuarios", "pages/usuarios.py", submenu=True)

    st.divider()

