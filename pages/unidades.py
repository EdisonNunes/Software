import pandas as pd
import streamlit as st

from components.page_banner import render_page_title_banner
from components.session_state import ensure_session_state
from components.sidebar import render_app_sidebar
from components.top_menu import render_top_menu
from pages.crud import (
    alterar_unidade,
    desativar_unidade,
    incluir_unidade,
    listar_todos_dados_unidades,
    reativar_unidade,
)


if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

render_app_sidebar()
render_top_menu()
render_page_title_banner("Cadastro de Unidades", icon_html="&#128208;")

ensure_session_state(
    {
        "unid_aba": "Listar",
        "unid_pagina": 0,
        "unid_busca": "",
        "unid_selecionada": None,
    }
)

PAGE_SIZE = 10


def _normalizar(texto: str) -> str:
    return (texto or "").strip().lower()


def _categorias_existentes() -> list[str]:
    dados = listar_todos_dados_unidades(ativo=None)
    categorias = []
    for item in dados:
        categoria = (item.get("categoria") or "").strip()
        if categoria and categoria not in categorias:
            categorias.append(categoria)

    for padrao in ["Tempo", "Producao", "Quantidade", "Embalagem", "Massa", "Volume"]:
        if padrao not in categorias:
            categorias.append(padrao)

    categorias.sort()
    return categorias


if st.session_state.unid_aba == "Listar":
    busca = st.text_input("Buscar unidade (codigo, descricao ou categoria)", st.session_state.unid_busca)
    if busca != st.session_state.unid_busca:
        st.session_state.unid_busca = busca
        st.session_state.unid_pagina = 0
        st.rerun()

    unidades = listar_todos_dados_unidades(ativo=None)

    busca_norm = _normalizar(st.session_state.unid_busca)
    if busca_norm:
        unidades = [
            item for item in unidades
            if busca_norm in _normalizar(item.get("codigo"))
            or busca_norm in _normalizar(item.get("descricao"))
            or busca_norm in _normalizar(item.get("categoria"))
        ]

    total = len(unidades)
    inicio = st.session_state.unid_pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE
    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

    if unidades:
        unidades_paginadas = unidades[inicio:fim]
        df_exibicao = pd.DataFrame(unidades_paginadas).copy()
        df_exibicao["Selecionar"] = False
        df_exibicao["situacao"] = df_exibicao["ativo"].apply(
            lambda v: "🟢 Ativa" if v else "🔴 Inativa"
        )

        selecao = st.data_editor(
            df_exibicao[["Selecionar", "categoria", "codigo", "descricao", "situacao"]].reset_index(drop=True),
            hide_index=True,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Selecionar"),
                "categoria": st.column_config.TextColumn("Categoria"),
                "codigo": st.column_config.TextColumn("Codigo"),
                "descricao": st.column_config.TextColumn("Descricao"),
                "situacao": st.column_config.TextColumn("Situacao"),
            },
            key="unidades_grid_unidades",
        )

        selecionados = selecao[selecao["Selecionar"] == True]
        if len(selecionados) == 1:
            idx = selecionados.index[0]
            if idx < len(unidades_paginadas):
                st.session_state.unid_selecionada = unidades_paginadas[idx]
        elif len(selecionados) > 1:
            st.error("Selecione apenas 1 unidade por vez.")

    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    if col_pag1.button("⬅️", disabled=st.session_state.unid_pagina <= 0):
        st.session_state.unid_pagina -= 1
        st.rerun()
    col_pag2.write(f"Pagina {st.session_state.unid_pagina + 1} de {total_paginas}")
    if col_pag3.button("➡️", disabled=(st.session_state.unid_pagina + 1) >= total_paginas):
        st.session_state.unid_pagina += 1
        st.rerun()

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Listar"):
            st.session_state.unid_aba = "Listar"
            st.rerun()
        if col2.button("Incluir"):
            st.session_state.unid_aba = "Incluir"
            st.rerun()
        if col3.button("Alterar", disabled=st.session_state.unid_selecionada is None):
            st.session_state.unid_aba = "Alterar"
            st.rerun()

        unidade_sel = st.session_state.unid_selecionada
        if unidade_sel is None:
            col4.button("🔒 Desativar", disabled=True)
        elif unidade_sel.get("ativo", True):
            if col4.button("🔒 Desativar"):
                try:
                    desativar_unidade(unidade_sel.get("id"))
                    st.session_state.unid_selecionada = None
                    st.success("Unidade desativada com sucesso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao desativar unidade: {e}")
        else:
            if col4.button("🔓 Reativar"):
                try:
                    reativar_unidade(unidade_sel.get("id"))
                    st.session_state.unid_selecionada = None
                    st.success("Unidade reativada com sucesso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao reativar unidade: {e}")

elif st.session_state.unid_aba == "Incluir":
    st.subheader("Incluir Unidade")

    categorias = _categorias_existentes()
    categoria_padrao = "Tempo" if "Tempo" in categorias else categorias[0]

    with st.form("form_incluir_unidade"):
        col1, col2 = st.columns([1, 2])
        with col1:
            codigo = st.text_input("Codigo", max_chars=20)
            categoria = st.selectbox("Categoria", categorias, index=categorias.index(categoria_padrao))
        with col2:
            descricao = st.text_input("Descricao", max_chars=255)
            ativo = st.checkbox("Unidade ativa", value=True)

        btn1, btn2 = st.columns(2)
        salvar = btn1.form_submit_button("Salvar", width='stretch')
        cancelar = btn2.form_submit_button("Sair sem Salvar", width='stretch')

        if cancelar:
            st.session_state.unid_aba = "Listar"
            st.rerun()

        if salvar:
            try:
                incluir_unidade(codigo, descricao, categoria, ativo=ativo)
                st.success("Unidade incluida com sucesso!")
                st.session_state.unid_selecionada = None
                st.session_state.unid_aba = "Listar"
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao incluir unidade: {e}")

elif st.session_state.unid_aba == "Alterar":
    st.subheader("Alterar Unidade")
    unidade = st.session_state.unid_selecionada

    if unidade is None:
        st.warning("Selecione uma unidade na lista antes de alterar.")
        if st.button("Voltar para lista"):
            st.session_state.unid_aba = "Listar"
            st.rerun()
    else:
        categorias = _categorias_existentes()
        categoria_atual = unidade.get("categoria")
        if categoria_atual not in categorias:
            categorias.append(categoria_atual)
        categorias = sorted(categorias)

        with st.form("form_alterar_unidade"):
            col1, col2 = st.columns([1, 2])
            with col1:
                codigo = st.text_input("Codigo", value=unidade.get("codigo", ""), max_chars=20)
                categoria = st.selectbox(
                    "Categoria",
                    categorias,
                    index=categorias.index(categoria_atual),
                )
            with col2:
                descricao = st.text_input("Descricao", value=unidade.get("descricao", ""), max_chars=255)
                ativo = st.checkbox("Unidade ativa", value=bool(unidade.get("ativo", True)))

            btn1, btn2 = st.columns(2)
            salvar = btn1.form_submit_button("Salvar", width='stretch')
            cancelar = btn2.form_submit_button("Cancelar", width='stretch')

            if cancelar:
                st.session_state.unid_aba = "Listar"
                st.rerun()

            if salvar:
                try:
                    alterar_unidade(unidade.get("id"), codigo, descricao, categoria, ativo=ativo)
                    st.success("Unidade alterada com sucesso!")
                    st.session_state.unid_selecionada = None
                    st.session_state.unid_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao alterar unidade: {e}")
