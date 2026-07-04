import pandas as pd
import streamlit as st

from components.page_banner import render_cliente_banner, render_page_title_banner
from components.session_state import ensure_session_state
from components.sidebar import render_app_sidebar
from components.top_menu import render_top_menu
from pages.crud import (
    alterar_familia_produto,
    desativar_familia_produto,
    incluir_familia_produto,
    listar_clientes,
    listar_familias_produtos,
    reativar_familia_produto,
)


if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

render_app_sidebar()
render_top_menu()
render_page_title_banner("Cadastro de Familias de Produto", icon_html="&#129533;")

ensure_session_state(
    {
        "fam_aba": "Listar",
        "fam_pagina": 0,
        "fam_busca_cliente": "",
        "fam_cliente_pagina": 0,
        "fam_cliente_selecionado": None,
        "fam_selecionada": None,
    }
)

if st.session_state.get("role") not in ["admin", "supervisor"]:
    if st.session_state.fam_cliente_selecionado is None and st.session_state.get("cliente"):
        st.session_state.fam_cliente_selecionado = st.session_state.cliente

PAGE_SIZE = 10


if st.session_state.fam_aba == "Listar":
    if st.session_state.get("role") in ["admin", "supervisor"]:
        busca = st.text_input("Buscar cliente", st.session_state.fam_busca_cliente)
        if busca != st.session_state.fam_busca_cliente:
            st.session_state.fam_busca_cliente = busca
            st.session_state.fam_cliente_pagina = 0
            st.session_state.fam_pagina = 0
            st.rerun()

    if st.session_state.fam_cliente_selecionado is None:
        if st.session_state.get("role") in ["admin", "supervisor"]:
            clientes = listar_clientes(filtro_empresa=st.session_state.fam_busca_cliente)
            total = len(clientes)
            inicio = st.session_state.fam_cliente_pagina * PAGE_SIZE
            fim = inicio + PAGE_SIZE
            st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

            if clientes:
                clientes_paginados = clientes[inicio:fim]
                df_clientes = pd.DataFrame(clientes_paginados).copy()
                df_clientes["Selecionar"] = False

                selecao_cli = st.data_editor(
                    df_clientes[["Selecionar", "empresa", "cidade", "telefone", "contato"]].reset_index(drop=True),
                    hide_index=True,
                    column_config={
                        "Selecionar": st.column_config.CheckboxColumn("Selecionar"),
                        "empresa": st.column_config.TextColumn("Empresa"),
                        "cidade": st.column_config.TextColumn("Cidade"),
                        "telefone": st.column_config.TextColumn("Telefone"),
                        "contato": st.column_config.TextColumn("Contato"),
                    },
                    key="familias_grid_clientes",
                )

                selecionados_cli = selecao_cli[selecao_cli["Selecionar"] == True]
                if len(selecionados_cli) == 1:
                    idx = selecionados_cli.index[0]
                    if idx < len(clientes_paginados):
                        st.session_state.fam_cliente_selecionado = clientes_paginados[idx]
                        st.session_state.fam_pagina = 0
                        st.rerun()
                elif len(selecionados_cli) > 1:
                    st.error("Selecione apenas 1 cliente por vez.")

            col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
            total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            if col_pag1.button("⬅️", disabled=st.session_state.fam_cliente_pagina <= 0):
                st.session_state.fam_cliente_pagina -= 1
                st.rerun()
            col_pag2.write(f"Pagina {st.session_state.fam_cliente_pagina + 1} de {total_paginas}")
            if col_pag3.button("➡️", disabled=(st.session_state.fam_cliente_pagina + 1) >= total_paginas):
                st.session_state.fam_cliente_pagina += 1
                st.rerun()

            st.stop()
        else:
            st.error("Empresa do usuario nao encontrada.")
            st.stop()

    cliente = st.session_state.fam_cliente_selecionado
    # O cliente selecionado vem de clientes (id); mantemos cliente_id apenas como fallback.
    cliente_id = cliente.get("id") or cliente.get("cliente_id")
    familias = listar_familias_produtos(cliente_id, ativo=None)

    if st.session_state.get("role") in ["admin", "supervisor"]:
        render_cliente_banner(cliente, len(familias), total_label="Familias")
        if st.button("Limpar selecao de cliente"):
            st.session_state.fam_cliente_selecionado = None
            st.session_state.fam_selecionada = None
            st.rerun()

    total = len(familias)
    inicio = st.session_state.fam_pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE
    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

    if familias:
        familias_paginadas = familias[inicio:fim]
        df_exibicao = pd.DataFrame(familias_paginadas).copy()
        df_exibicao["Selecionar"] = False
        df_exibicao["situacao"] = df_exibicao["ativo"].apply(
            lambda v: "🟢 Ativa" if v else "🔴 Inativa"
        )

        selecao = st.data_editor(
            df_exibicao[["Selecionar", "codigo", "descricao", "situacao"]].reset_index(drop=True),
            hide_index=True,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Selecionar"),
                "codigo": st.column_config.TextColumn("Codigo"),
                "descricao": st.column_config.TextColumn("Descricao"),
                "situacao": st.column_config.TextColumn("Situacao"),
            },
            key="familias_grid_familias",
        )

        selecionados = selecao[selecao["Selecionar"] == True]
        if len(selecionados) == 1:
            idx = selecionados.index[0]
            if idx < len(familias_paginadas):
                st.session_state.fam_selecionada = familias_paginadas[idx]
        elif len(selecionados) > 1:
            st.error("Selecione apenas 1 familia por vez.")
    else:
        st.info("Nenhuma família encontrada para o cliente selecionado.")

    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    if col_pag1.button("⬅️", disabled=st.session_state.fam_pagina <= 0):
        st.session_state.fam_pagina -= 1
        st.rerun()
    col_pag2.write(f"Pagina {st.session_state.fam_pagina + 1} de {total_paginas}")
    if col_pag3.button("➡️", disabled=(st.session_state.fam_pagina + 1) >= total_paginas):
        st.session_state.fam_pagina += 1
        st.rerun()

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Listar"):
            st.session_state.fam_aba = "Listar"
            st.rerun()
        if col2.button("Incluir"):
            st.session_state.fam_aba = "Incluir"
            st.rerun()
        if col3.button("Alterar", disabled=st.session_state.fam_selecionada is None):
            st.session_state.fam_aba = "Alterar"
            st.rerun()

        familia_sel = st.session_state.fam_selecionada
        if familia_sel is None:
            col4.button("🔒 Desativar", disabled=True)
        elif familia_sel.get("ativo", True):
            if col4.button("🔒 Desativar"):
                try:
                    desativar_familia_produto(familia_sel.get("id"))
                    st.session_state.fam_selecionada = None
                    st.success("Familia desativada com sucesso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao desativar familia: {e}")
        else:
            if col4.button("🔓 Reativar"):
                try:
                    reativar_familia_produto(familia_sel.get("id"))
                    st.session_state.fam_selecionada = None
                    st.success("Familia reativada com sucesso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao reativar familia: {e}")

elif st.session_state.fam_aba == "Incluir":
    st.subheader("Incluir Familia de Produto")

    if st.session_state.fam_cliente_selecionado is None:
        st.warning("Selecione um cliente antes de incluir uma familia.")
        if st.button("Escolher cliente"):
            st.session_state.fam_aba = "Listar"
            st.rerun()
    else:
        cliente = st.session_state.fam_cliente_selecionado
        cliente_id = cliente.get("id") or cliente.get("cliente_id")
        st.text_input("Cliente", value=cliente.get("empresa", ""), disabled=True)

        with st.form("form_incluir_familia"):
            codigo = st.text_input("Codigo", max_chars=30)
            descricao = st.text_input("Descricao", max_chars=255)
            ativo = st.checkbox("Familia ativa", value=True)

            col1, col2 = st.columns(2)
            salvar = col1.form_submit_button("Salvar", width='stretch')
            cancelar = col2.form_submit_button("Sair sem Salvar", width='stretch')

            if cancelar:
                st.session_state.fam_aba = "Listar"
                st.rerun()

            if salvar:
                try:
                    incluir_familia_produto(codigo, descricao, cliente_id, ativo=ativo)
                    st.success("Familia incluida com sucesso!")
                    st.session_state.fam_selecionada = None
                    st.session_state.fam_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao incluir familia: {e}")

elif st.session_state.fam_aba == "Alterar":
    st.subheader("Alterar Familia de Produto")
    familia = st.session_state.fam_selecionada

    if familia is None:
        st.warning("Selecione uma familia na lista antes de alterar.")
        if st.button("Voltar para lista"):
            st.session_state.fam_aba = "Listar"
            st.rerun()
    else:
        cliente = st.session_state.fam_cliente_selecionado
        st.text_input("Cliente", value=(cliente or {}).get("empresa", ""), disabled=True)

        with st.form("form_alterar_familia"):
            codigo = st.text_input("Codigo", value=familia.get("codigo", ""), max_chars=30)
            descricao = st.text_input("Descricao", value=familia.get("descricao", ""), max_chars=255)
            ativo = st.checkbox("Familia ativa", value=bool(familia.get("ativo", True)))

            col1, col2 = st.columns(2)
            salvar = col1.form_submit_button("Salvar", width='stretch')
            cancelar = col2.form_submit_button("Cancelar", width='stretch')

            if cancelar:
                st.session_state.fam_aba = "Listar"
                st.rerun()

            if salvar:
                try:
                    alterar_familia_produto(
                        familia.get("id"),
                        codigo,
                        descricao,
                        ativo=ativo,
                    )
                    st.success("Familia alterada com sucesso!")
                    st.session_state.fam_selecionada = None
                    st.session_state.fam_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao alterar familia: {e}")
