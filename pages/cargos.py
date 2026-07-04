import pandas as pd
import streamlit as st

from components.page_banner import render_page_title_banner
from components.session_state import ensure_session_state
from components.sidebar import render_app_sidebar
from components.top_menu import render_top_menu
from pages.crud import (
    alterar_cargo,
    desativar_cargo,
    incluir_cargo,
    listar_cargos,
    reativar_cargo,
)


if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

render_app_sidebar()
render_top_menu()
render_page_title_banner("Cadastro de Cargos", icon_html="&#128188;")

ensure_session_state(
    {
        "cargo_aba": "Listar",
        "cargo_pagina": 0,
        "cargo_busca": "",
        "cargo_selecionado": None,
    }
)

PAGE_SIZE = 10


def _normalizar(texto: str) -> str:
    return (texto or "").strip().lower()


def _retornar_para_usuarios() -> None:
    if st.session_state.get("usuarios_retorno_apos_cargo"):
        st.session_state.usuarios_retorno_apos_cargo = False
        st.session_state.usuarios_aba = "Listar"
        st.session_state.usuarios_usuario_selecionado = None
        st.switch_page("pages/usuarios.py")


if st.session_state.cargo_aba == "Listar":
    busca = st.text_input("Buscar cargo", st.session_state.cargo_busca)
    if busca != st.session_state.cargo_busca:
        st.session_state.cargo_busca = busca
        st.session_state.cargo_pagina = 0
        st.rerun()

    cargos = listar_cargos(ativo=None)
    busca_norm = _normalizar(st.session_state.cargo_busca)
    if busca_norm:
        cargos = [item for item in cargos if busca_norm in _normalizar(item.get("descricao"))]

    total = len(cargos)
    inicio = st.session_state.cargo_pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE
    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

    if cargos:
        cargos_paginados = cargos[inicio:fim]
        df_exibicao = pd.DataFrame(cargos_paginados).copy()
        df_exibicao["Selecionar"] = False
        df_exibicao["situacao"] = df_exibicao["ativo"].apply(
            lambda v: "🟢 Ativo" if v else "🔴 Inativo"
        )

        selecao = st.data_editor(
            df_exibicao[["Selecionar", "descricao", "situacao"]].reset_index(drop=True),
            hide_index=True,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Selecionar"),
                "descricao": st.column_config.TextColumn("Cargo"),
                "situacao": st.column_config.TextColumn("Situacao"),
            },
            key="cargos_grid_cargos",
        )

        selecionados = selecao[selecao["Selecionar"] == True]
        if len(selecionados) == 1:
            idx = selecionados.index[0]
            if idx < len(cargos_paginados):
                st.session_state.cargo_selecionado = cargos_paginados[idx]
        elif len(selecionados) > 1:
            st.error("Selecione apenas 1 cargo por vez.")

    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    if col_pag1.button("⬅️", disabled=st.session_state.cargo_pagina <= 0):
        st.session_state.cargo_pagina -= 1
        st.rerun()
    col_pag2.write(f"Pagina {st.session_state.cargo_pagina + 1} de {total_paginas}")
    if col_pag3.button("➡️", disabled=(st.session_state.cargo_pagina + 1) >= total_paginas):
        st.session_state.cargo_pagina += 1
        st.rerun()

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Listar"):
            st.session_state.cargo_aba = "Listar"
            st.rerun()
        if col2.button("Incluir"):
            st.session_state.cargo_aba = "Incluir"
            st.rerun()
        if col3.button("Alterar", disabled=st.session_state.cargo_selecionado is None):
            st.session_state.cargo_aba = "Alterar"
            st.rerun()

        cargo_sel = st.session_state.cargo_selecionado
        if cargo_sel is None:
            col4.button("🔒 Desativar", disabled=True)
        elif cargo_sel.get("ativo", True):
            if col4.button("🔒 Desativar"):
                try:
                    desativar_cargo(cargo_sel.get("id"))
                    st.session_state.cargo_selecionado = None
                    st.success("Cargo desativado com sucesso.")
                    _retornar_para_usuarios()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao desativar cargo: {e}")
        else:
            if col4.button("🔓 Reativar"):
                try:
                    reativar_cargo(cargo_sel.get("id"))
                    st.session_state.cargo_selecionado = None
                    st.success("Cargo reativado com sucesso.")
                    _retornar_para_usuarios()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao reativar cargo: {e}")

elif st.session_state.cargo_aba == "Incluir":
    st.subheader("Incluir Cargo")

    with st.form("form_incluir_cargo"):
        descricao = st.text_input("Descricao", max_chars=120)
        ativo = st.checkbox("Cargo ativo", value=True)

        col1, col2 = st.columns(2)
        salvar = col1.form_submit_button("Salvar", width='stretch')
        cancelar = col2.form_submit_button("Sair sem Salvar", width='stretch')

        if cancelar:
            st.session_state.cargo_aba = "Listar"
            st.rerun()

        if salvar:
            try:
                incluir_cargo(descricao, ativo=ativo)
                st.success("Cargo incluido com sucesso!")
                st.session_state.cargo_selecionado = None
                _retornar_para_usuarios()
                st.session_state.cargo_aba = "Listar"
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao incluir cargo: {e}")

elif st.session_state.cargo_aba == "Alterar":
    st.subheader("Alterar Cargo")
    cargo = st.session_state.cargo_selecionado

    if cargo is None:
        st.warning("Selecione um cargo na lista antes de alterar.")
        if st.button("Voltar para lista"):
            st.session_state.cargo_aba = "Listar"
            st.rerun()
    else:
        with st.form("form_alterar_cargo"):
            descricao = st.text_input("Descricao", value=cargo.get("descricao", ""), max_chars=120)
            ativo = st.checkbox("Cargo ativo", value=bool(cargo.get("ativo", True)))

            col1, col2 = st.columns(2)
            salvar = col1.form_submit_button("Salvar", width='stretch')
            cancelar = col2.form_submit_button("Cancelar", width='stretch')

            if cancelar:
                st.session_state.cargo_aba = "Listar"
                st.rerun()

            if salvar:
                try:
                    alterar_cargo(cargo.get("id"), descricao, ativo=ativo)
                    st.success("Cargo alterado com sucesso!")
                    st.session_state.cargo_selecionado = None
                    _retornar_para_usuarios()
                    st.session_state.cargo_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao alterar cargo: {e}")
