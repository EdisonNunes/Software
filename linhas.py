# Admin e Supervisor veem tudo.
# Gerente e Funcionário veem apenas as áreas da própria empresa

import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd
import streamlit.components.v1 as components

from crud import listar_clientes, listar_todos_dados_clientes
from crud import listar_linhas, listar_todos_dados_linhas, incluir_linha, alterar_linha, excluir_linha
st.info(f'# Cadastro de Linhas de Produção',icon=':material/conveyor_belt:')

if "linha_aba" not in st.session_state:
    st.session_state.linha_aba = "Listar"

if "linha_pagina" not in st.session_state:
    st.session_state.linha_pagina = 0

if "linha_busca_descricao" not in st.session_state:
    st.session_state.linha_busca_descricao = ""

if "linha_selecionada" not in st.session_state:
    st.session_state.linha_selecionada = None

if "linha_cliente_selecionado" not in st.session_state:
    st.session_state.linha_cliente_selecionado = None

if "linha_cliente_pagina" not in st.session_state:
    st.session_state.linha_cliente_pagina = 0


PAGE_SIZE = 10

if st.session_state.linha_aba == "Listar":
    # Se nenhum cliente selecionado, primeiro mostrar grid de clientes
    busca_atual = st.text_input("Buscar cliente", st.session_state.linha_busca_descricao)
    if busca_atual != st.session_state.linha_busca_descricao:
        st.session_state.linha_busca_descricao = busca_atual
        st.session_state.linha_cliente_pagina = 0
        st.session_state.linha_pagina = 0
        st.rerun()

    #print("st.session_state.linha_cliente_selecionado:", st.session_state.linha_cliente_selecionado)
    if st.session_state.linha_cliente_selecionado is None: 
        # Admin e Supervisor escolhem a empresa

        #print("st.session_state.get('role'):", st.session_state.get("role"))
        if st.session_state.get("role") in ["admin", "supervisor"]:                                       
            clientes = listar_clientes(filtro_empresa=st.session_state.linha_busca_descricao)
            total = len(clientes)
            inicio = st.session_state.linha_cliente_pagina * PAGE_SIZE
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
                    key="grid_clientes"
                )

                selecionados_cli = selecao_cli[selecao_cli["Selecionar"] == True]
                if len(selecionados_cli) == 1:
                    idx = selecionados_cli.index[0]
                    if idx < len(clientes_paginados):
                        id_selecionado = clientes_paginados[idx].get("id") or clientes_paginados[idx].get("id_cliente")
                        cliente_completo = next((c for c in listar_todos_dados_clientes() if (c.get("id") == id_selecionado or c.get("id_cliente") == id_selecionado)), None)
                        if cliente_completo:
                            st.session_state.linha_cliente_selecionado = cliente_completo
                            st.session_state.linha_pagina = 0
                            st.rerun()
                elif len(selecionados_cli) > 1:
                    st.error("Selecione apenas 1 cliente por vez.")

            # Paginação de clientes
            col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
            total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            if col_pag1.button("⬅️", disabled=st.session_state.linha_cliente_pagina <= 0):
                st.session_state.linha_cliente_pagina -= 1
                st.rerun()
            col_pag2.write(f"Página {st.session_state.linha_cliente_pagina + 1} de {total_paginas}")
            if col_pag3.button("➡️", disabled=(st.session_state.linha_cliente_pagina + 1) >= total_paginas):
                st.session_state.linha_cliente_pagina += 1
                st.rerun()

            # Não mostrar botões de ação antes da seleção do cliente
            st.stop()
       # Gerente e Funcionário usam automaticamente sua empresa
        else:
            cliente_completo = next((c for c in listar_todos_dados_clientes()
                    if c.get("id") == st.session_state.get("cliente_id")), None)

            if cliente_completo:
                st.session_state.linha_cliente_selecionado = (cliente_completo)
                st.rerun()

    # Se chegou aqui, há um cliente selecionado: mostrar Linhas apenas deste cliente
    cliente = st.session_state.linha_cliente_selecionado
    if cliente and st.session_state.get("role") in ["admin", "supervisor"]:
        st.success(f"# Linhas da empresa   :point_right: {cliente.get('empresa')}",icon=':material/conveyor_belt:')
        if st.button("Limpar seleção de cliente"):
            st.session_state.linha_cliente_selecionado = None
            st.rerun()

    linhas = listar_linhas(cliente.get('id') or cliente.get('id_cliente'))
    total = len(linhas)
    inicio = st.session_state.linha_pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE
    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

    if linhas:
        linhas_paginados = linhas[inicio:fim]
        df_exibicao = pd.DataFrame(linhas_paginados).copy()
        df_exibicao["Selecionar"] = False
        # df_exibicao["id_produto"] = df_exibicao["id_produto"].astype(str)

        # Colunas e Configuração
        cols_exibicao = ["Selecionar", "codigo", "descricao", "responsavel"]
        
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
                "responsavel": st.column_config.TextColumn(
                    "Responsável"
                )
            },
            key="grid_linhas"
        )

        # Lógica de Seleção
        selecionados = selecao[selecao["Selecionar"] == True]

        if len(selecionados) == 1:
            idx_paginado = selecionados.index[0]
            if idx_paginado < len(linhas_paginados):
                id_selecionado = linhas_paginados[idx_paginado].get("id")

                linha_completa = next((c for c in listar_todos_dados_linhas() if c.get("id") == id_selecionado), None)

                if linha_completa:
                    st.session_state.linha_selecionada = linha_completa
        elif len(selecionados) > 1:
            st.error("Selecione apenas 1 linha por vez.")
        else:
            st.session_state.linha_selecionada = None

    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    
    total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    if col_pag1.button("⬅️", disabled=st.session_state.linha_pagina <= 0):
        st.session_state.linha_pagina -= 1
        st.rerun()

    col_pag2.write(f"Página {st.session_state.linha_pagina + 1} de {total_paginas}")

    if col_pag3.button("➡️", disabled=(st.session_state.linha_pagina + 1) >= total_paginas):
        st.session_state.linha_pagina += 1
        st.rerun()

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Listar"):
            st.session_state.linha_aba = "Listar"
            st.rerun()
        if col2.button("Incluir"):
            st.session_state.linha_aba = "Incluir"
            st.rerun()
        if col3.button("Alterar"):
            st.session_state.linha_aba = "Alterar"
            st.rerun()
        if col4.button("Excluir"):
            st.session_state.linha_aba = "Excluir"
elif st.session_state.linha_aba == "Incluir":
    st.subheader("Incluir Linha")

    # Verifica se há cliente selecionado
    if st.session_state.linha_cliente_selecionado is None:
        st.warning("Selecione um cliente antes de incluir um produto.")
        if st.button("Escolher cliente"):
            st.session_state.linha_aba = "Listar"
            st.rerun()
    else:
        cliente = st.session_state.linha_cliente_selecionado
        # Exibir via componente HTML para garantir que estilo seja aplicado
        html = f"""
        <style>
          .selected-client {{ color: orange !important; font-size:28px !important; font-weight:700 !important; margin:6px 0; }}
        </style>
        <div class="selected-client">Cliente selecionado: {cliente.get('empresa')}</div>
        """
        components.html(html, height=60)

        # Formulário aprimorado em colunas
        with st.form("form_incluir_linha"):
            # Campo não editável com o cliente selecionado
            # st.text_input("Cliente", value=cliente.get('empresa'), disabled=True)
            codigo = st.text_input("Código", max_chars=50)
            descricao = st.text_input("Descrição", max_chars=255)
            responsavel = st.text_input("Responsável", max_chars=255)

           # Botões lado-a-lado: Salvar e Sair sem Salvar
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar")
            with btn_col2:
                sair_sem_salvar = st.form_submit_button("Sair sem Salvar")

            if sair_sem_salvar:
                # Abandonar inclusão e voltar para seleção de cliente
                st.session_state.linha_cliente_selecionado = None
                st.session_state.linha_aba = "Listar"
                st.rerun()

            if salvar:
                cliente_id = (
                                cliente.get("id")
                                or cliente.get("id_cliente")
)
                try:
                    incluir_linha(codigo, descricao, responsavel, cliente_id)
                    st.success("Linha incluída com sucesso!")
                    # Limpar seleção de linha e voltar para listagem
                    st.session_state.linha_selecionada = None
                    st.session_state.linha_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao incluir linha: {e}")

elif st.session_state.linha_aba == "Alterar":
    st.subheader("Alterar Linha")

    if st.session_state.linha_selecionada is None:
        st.warning("Selecione uma linha na lista antes de alterar.")
        if st.button("Voltar para lista"):
            st.session_state.linha_aba = "Listar"
            st.rerun()
    else:
        linha = st.session_state.linha_selecionada
        cliente = st.session_state.linha_cliente_selecionado

        # Mostrar cliente não editável
        st.text_input("Cliente", value=cliente.get('empresa'), disabled=True)

        # Form para alterar
        with st.form("form_alterar_linha"):
            col1, col2 = st.columns([2, 1])
            with col1:
                codigo = st.text_input("Código", value=linha.get('codigo', ''), max_chars=50)
                descricao = st.text_input("Descrição", value=linha.get('descricao', ''), max_chars=255)
                responsavel = st.text_input("Responsável", value=linha.get('responsavel', ''), max_chars=255)
                # Ações
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar Alterações")
            with btn_col2:
                cancelar = st.form_submit_button("Cancelar")

            if cancelar:
                st.session_state.linha_selecionada = None
                st.session_state.linha_aba = "Listar"
                st.rerun()

            if salvar:
                cliente_id = (
                    cliente.get("id")
                    or cliente.get("id_cliente")
                )

                try:
                    linha_id = linha.get('id')
                    alterar_linha(linha_id, codigo, descricao, responsavel)
                    st.success("Linha alterada com sucesso!")
                    st.session_state.linha_selecionada = None
                    st.session_state.linha_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao alterar linha: {e}")

elif st.session_state.linha_aba == "Excluir":
    st.subheader("Excluir Linha")

    if st.session_state.linha_selecionada is None:
        st.warning("Selecione uma linha na lista antes de excluir.")
        if st.button("Voltar para lista"):
            st.session_state.linha_aba = "Listar"
            st.rerun()
    else:
        linha = st.session_state.linha_selecionada
        st.markdown(f"**Linha selecionada:** {linha.get('descricao')} ({linha.get('codigo')})")
        col_confirm, col_cancel = st.columns([1, 1])
        if col_cancel.button("Cancelar"):
            st.session_state.linha_selecionada = None
            st.session_state.linha_aba = "Listar"
            st.rerun()

        if col_confirm.button("Confirmar Exclusão ?"):
            try:
                linha_id = linha.get("id")
                excluir_linha(linha_id)
                st.success("Linha excluída com sucesso")
                st.session_state.linha_selecionada = None
                st.session_state.linha_aba = "Listar"
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao excluir linha: {e}")