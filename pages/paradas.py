# Admin e Supervisor veem tudo.
# Gerente e Funcionário veem apenas as áreas da própria empresa

import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd
import streamlit.components.v1 as components

from pages.crud import listar_clientes
from pages.crud import listar_paradas, listar_todos_dados_paradas, incluir_parada, alterar_parada, excluir_parada

from components.top_menu import render_top_menu
from components.sidebar import render_app_sidebar
from components.session_state import ensure_session_state

if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

render_app_sidebar()
    
render_top_menu()

st.info(f'# Cadastro de paradas de Produção',icon=':material/conveyor_belt:')

ensure_session_state(
    {
        "parada_aba": "Listar",
        "parada_pagina": 0,
        "parada_busca_descricao": "",
        "parada_selecionada": None,
        "parada_cliente_selecionado": None,
        "parada_cliente_pagina": 0,
    }
)

if (st.session_state.get("role") not in ["admin", "supervisor"]):
   if (st.session_state.parada_cliente_selecionado is None and st.session_state.get("cliente")):
        st.session_state.parada_cliente_selecionado = st.session_state.cliente

PAGE_SIZE = 10

if st.session_state.parada_aba == "Listar":
    # Se nenhum cliente selecionado, primeiro mostrar grid de clientes
    busca_atual = st.text_input("Buscar cliente", st.session_state.parada_busca_descricao)
    if busca_atual != st.session_state.parada_busca_descricao:
        st.session_state.parada_busca_descricao = busca_atual
        st.session_state.parada_cliente_pagina = 0
        st.session_state.parada_pagina = 0
        st.rerun()

    if st.session_state.parada_cliente_selecionado is None: 
        # Admin e Supervisor escolhem a empresa
        if st.session_state.get("role") in ["admin", "supervisor"]:                                       
            clientes = listar_clientes(filtro_empresa=st.session_state.parada_busca_descricao)
            total = len(clientes)
            inicio = st.session_state.parada_cliente_pagina * PAGE_SIZE
            fim = inicio + PAGE_SIZE
            st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

            if clientes:
                clientes_paginados = clientes[inicio:fim]
                df_clientes = pd.DataFrame(clientes_paginados).copy()
                df_clientes["Selecionar"] = False

                cols_clientes = ["Selecionar", "empresa", "cidade", "telefone", "contato"]

                selecao_cli = st.data_editor(
                    df_clientes[cols_clientes].reset_index(drop=True),
                    hide_index=True,
                    column_config={
                        "Selecionar": st.column_config.CheckboxColumn("Selecionar", help="Marque para selecionar"),
                        "empresa": st.column_config.TextColumn("Empresa"),
                        "cidade": st.column_config.TextColumn("Cidade"),
                        "telefone": st.column_config.TextColumn("Telefone"),
                        "contato": st.column_config.TextColumn("Contato"),
                    },
                    key="paradas_grid_clientes"
                )

                selecionados_cli = selecao_cli[selecao_cli["Selecionar"] == True]
                
                if len(selecionados_cli) == 1:
                    idx = selecionados_cli.index[0]
                    if idx < len(clientes_paginados):
                        st.session_state.parada_cliente_selecionado = (clientes_paginados[idx])
                        st.session_state.parada_pagina = 0
                        st.rerun()
                elif len(selecionados_cli) > 1:
                    st.error("Selecione apenas 1 cliente por vez.")

            # Paginação de clientes
            col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
            total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            if col_pag1.button("⬅️", disabled=st.session_state.parada_cliente_pagina <= 0):
                st.session_state.parada_cliente_pagina -= 1
                st.rerun()
            col_pag2.write(f"Página {st.session_state.parada_cliente_pagina + 1} de {total_paginas}")
            if col_pag3.button("➡️", disabled=(st.session_state.parada_cliente_pagina + 1) >= total_paginas):
                st.session_state.parada_cliente_pagina += 1
                st.rerun()

            # Não mostrar botões de ação antes da seleção do cliente
            st.stop()
        else:
            # Gerente e Funcionário usam automaticamente sua empresa
            if st.session_state.get("cliente"):
                st.session_state.parada_cliente_selecionado = (st.session_state.cliente)
                st.rerun()
            else:
                st.error("Empresa do usuário não encontrada.")
                st.stop()

    # Se chegou aqui, há um cliente selecionado: mostrar paradas apenas deste cliente
    cliente = st.session_state.parada_cliente_selecionado
    if cliente and st.session_state.get("role") in ["admin", "supervisor"]:
        st.success(f"# Paradas da empresa   :point_right: {cliente.get('empresa')}",icon=':material/conveyor_belt:')
        if st.button("Limpar seleção de cliente"):
            st.session_state.parada_cliente_selecionado = None
            st.rerun()

    if cliente:
        paradas = listar_paradas(cliente.get('id') or cliente.get('id_cliente'))
    else:
        paradas = []    
    total = len(paradas)
    inicio = st.session_state.parada_pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE
    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

    if paradas:
        paradas_paginados = paradas[inicio:fim]
        df_exibicao = pd.DataFrame(paradas_paginados).copy()
        df_exibicao["Selecionar"] = False
        # df_exibicao["id_produto"] = df_exibicao["id_produto"].astype(str)

        # Colunas e Configuração
        cols_exibicao = ["Selecionar", "codigo", "descricao", "categoria_oee"]
        
        selecao = st.data_editor(
            df_exibicao[cols_exibicao].reset_index(drop=True),
            hide_index=True,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn(
                    "Selecionar"
                ),
                "codigo": st.column_config.TextColumn(
                    "Código"
                ),
                "descricao": st.column_config.TextColumn(
                    "Descrição"
                ),
                "categoria_oee": st.column_config.TextColumn(
                    "Categoria OEE"
                )
            },
            key="paradas_grid_paradas"
        )

        # Lógica de Seleção
        selecionados = selecao[selecao["Selecionar"] == True]

        if len(selecionados) == 1:
            idx_paginado = selecionados.index[0]
            if idx_paginado < len(paradas_paginados):
                id_selecionado = paradas_paginados[idx_paginado].get("id")

                parada_completa = next((c for c in listar_todos_dados_paradas() if c.get("id") == id_selecionado), None)

                if parada_completa:
                    st.session_state.parada_selecionada = parada_completa
        elif len(selecionados) > 1:
            st.error("Selecione apenas 1 parada por vez.")

    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    
    total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    if col_pag1.button("⬅️", disabled=st.session_state.parada_pagina <= 0):
        st.session_state.parada_pagina -= 1
        st.rerun()

    col_pag2.write(f"Página {st.session_state.parada_pagina + 1} de {total_paginas}")

    if col_pag3.button("➡️", disabled=(st.session_state.parada_pagina + 1) >= total_paginas):
        st.session_state.parada_pagina += 1
        st.rerun()

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Listar"):
            st.session_state.parada_aba = "Listar"
            st.rerun()
        if col2.button("Incluir"):
            st.session_state.parada_aba = "Incluir"
            st.rerun()
        if col3.button("Alterar", disabled=st.session_state.parada_selecionada is None):
            st.session_state.parada_aba = "Alterar"
            st.rerun()
        if col4.button("Excluir", disabled=st.session_state.parada_selecionada is None):
            st.session_state.parada_aba = "Excluir"
            st.rerun()
            
elif st.session_state.parada_aba == "Incluir":
    st.subheader("Incluir parada")

    # Verifica se há cliente selecionado
    if st.session_state.parada_cliente_selecionado is None:
        st.warning("Selecione um cliente antes de incluir um produto.")
        if st.button("Escolher cliente"):
            st.session_state.parada_aba = "Listar"
            st.rerun()
    else:
        cliente = st.session_state.parada_cliente_selecionado
        # Exibir via componente HTML para garantir que estilo seja aplicado
        html = f"""
        <style>
          .selected-client {{ color: orange !important; font-size:28px !important; font-weight:700 !important; margin:6px 0; }}
        </style>
        <div class="selected-client">Cliente selecionado: {cliente.get('empresa')}</div>
        """
        components.html(html, height=60)

        # Formulário aprimorado em colunas
        with st.form("form_incluir_parada"):
            # Campo não editável com o cliente selecionado
            # st.text_input("Cliente", value=cliente.get('empresa'), disabled=True)
            codigo = st.text_input("Código", max_chars=50)
            descricao = st.text_input("Descrição", max_chars=255)
            categorias_oee = ["Disponibilidade", "Performance", "Qualidade"]
            categoria_oee = st.selectbox("Categoria OEE", categorias_oee, width="stretch")

           # Botões lado-a-lado: Salvar e Sair sem Salvar
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar")
            with btn_col2:
                sair_sem_salvar = st.form_submit_button("Sair sem Salvar")

            if sair_sem_salvar:
                # Abandonar inclusão e voltar para seleção de cliente
                st.session_state.parada_cliente_selecionado = None
                st.session_state.parada_aba = "Listar"
                st.rerun()

            if salvar:
                cliente_id = (
                                cliente.get("id")
                                or cliente.get("id_cliente")
)
                try:
                    incluir_parada(codigo, descricao, categoria_oee, cliente_id)
                    st.success("Parada incluída com sucesso!")
                    # Limpar seleção de parada e voltar para listagem
                    st.session_state.parada_selecionada = None
                    st.session_state.parada_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao incluir parada: {e}")

elif st.session_state.parada_aba == "Alterar":
    st.subheader("Alterar Parada")

    if st.session_state.parada_selecionada is None:
        st.warning("Selecione uma parada na lista antes de alterar.")
        if st.button("Voltar para lista"):
            st.session_state.parada_aba = "Listar"
            st.rerun()
    else:
        parada = st.session_state.parada_selecionada
        cliente = st.session_state.parada_cliente_selecionado

        # Mostrar cliente não editável
        st.text_input("Cliente", value=cliente.get('empresa'), disabled=True)

        # Form para alterar
        with st.form("form_alterar_parada"):
            col1, col2 = st.columns([2, 1])
            with col1:
                codigo = st.text_input("Código", value=parada.get('codigo', ''), max_chars=50)
                descricao = st.text_input("Descrição", value=parada.get('descricao', ''), max_chars=255)
                categorias_oee = ["Disponibilidade", "Performance", "Qualidade"]
                categoria_atual = parada.get("categoria_oee") or parada.get("codigo_oee")
                if categoria_atual not in categorias_oee:
                    categoria_atual = categorias_oee[0]
                categoria_oee = st.selectbox(
                    "Categoria OEE",
                    categorias_oee,
                    index=categorias_oee.index(categoria_atual),
                    width="stretch",
                )
                # Ações
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar Alterações")
            with btn_col2:
                cancelar = st.form_submit_button("Cancelar")

            if cancelar:
                st.session_state.parada_selecionada = None
                st.session_state.parada_aba = "Listar"
                st.rerun()

            if salvar:
                cliente_id = (
                    cliente.get("id")
                    or cliente.get("id_cliente")
                )

                try:
                    parada_id = parada.get('id')
                    alterar_parada(parada_id, codigo, descricao, categoria_oee)
                    st.success("Parada alterada com sucesso!")
                    st.session_state.parada_selecionada = None
                    st.session_state.parada_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao alterar Parada: {e}")

elif st.session_state.parada_aba == "Excluir":
    st.subheader("Excluir Parada")

    if st.session_state.parada_selecionada is None:
        st.warning("Selecione uma parada na lista antes de excluir.")
        if st.button("Voltar para lista"):
            st.session_state.parada_aba = "Listar"
            st.rerun()
    else:
        parada = st.session_state.parada_selecionada
        st.markdown(f"**Parada selecionada:** {parada.get('descricao')} ({parada.get('codigo')})")
        col_confirm, col_cancel = st.columns([1, 1])
        if col_cancel.button("Cancelar"):
            st.session_state.parada_selecionada = None
            st.session_state.parada_aba = "Listar"
            st.rerun()

        if col_confirm.button("Confirmar Exclusão ?"):
            try:
                parada_id = parada.get("id")
                excluir_parada(parada_id)
                st.success("Parada excluída com sucesso")
                st.session_state.parada_selecionada = None
                st.session_state.parada_aba = "Listar"
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao excluir Parada: {e}")

