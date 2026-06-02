import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd
import streamlit.components.v1 as components

# from crud import supabase, listar_servicos,listar_todos_dados_servicos,incluir_servico,alterar_servico,excluir_servico, verificar_uso_servico
from crud import *
st.info(f'### Produtos Cadastrados',icon=':material/thermostat:')

if "aba" not in st.session_state:
    st.session_state.aba = "Listar"
if "pagina" not in st.session_state:
    st.session_state.pagina = 0
if "busca_descricao" not in st.session_state:
    st.session_state.busca_descricao = ""
if "produto_selecionado" not in st.session_state:
    st.session_state.produto_selecionado = None
if "cliente_selecionado" not in st.session_state:
    st.session_state.cliente_selecionado = None
if "cliente_pagina" not in st.session_state:
    st.session_state.cliente_pagina = 0


PAGE_SIZE = 10

if st.session_state.aba == "Listar":
    # Se nenhum cliente selecionado, primeiro mostrar grid de clientes
    busca_atual = st.text_input("Buscar cliente", st.session_state.busca_descricao)
    if busca_atual != st.session_state.busca_descricao:
        st.session_state.busca_descricao = busca_atual
        st.session_state.cliente_pagina = 0
        st.session_state.pagina = 0
        st.rerun()

    if st.session_state.cliente_selecionado is None:
        clientes = listar_clientes(filtro_empresa=st.session_state.busca_descricao)
        total = len(clientes)
        inicio = st.session_state.cliente_pagina * PAGE_SIZE
        fim = inicio + PAGE_SIZE
        st.write(f"Clientes: mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

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
                        st.session_state.cliente_selecionado = cliente_completo
                        st.session_state.pagina = 0
                        st.rerun()
            elif len(selecionados_cli) > 1:
                st.error("Selecione apenas 1 cliente por vez.")

        # Paginação de clientes
        col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
        total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        if col_pag1.button("⬅️", disabled=st.session_state.cliente_pagina <= 0):
            st.session_state.cliente_pagina -= 1
            st.rerun()
        col_pag2.write(f"Página {st.session_state.cliente_pagina + 1} de {total_paginas}")
        if col_pag3.button("➡️", disabled=(st.session_state.cliente_pagina + 1) >= total_paginas):
            st.session_state.cliente_pagina += 1
            st.rerun()

        # Não mostrar botões de ação antes da seleção do cliente
        st.stop()

    # Se chegou aqui, há um cliente selecionado: mostrar produtos apenas deste cliente
    cliente = st.session_state.cliente_selecionado
    st.write(f"Produtos do cliente: {cliente.get('empresa')}")
    if st.button("Limpar seleção de cliente"):
        st.session_state.cliente_selecionado = None
        st.rerun()

    produtos = listar_produtos(filtro_produto=cliente.get('id') or cliente.get('id_cliente'))
    total = len(produtos)
    inicio = st.session_state.pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE
    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

    if produtos:
        produtos_paginados = produtos[inicio:fim]
        df_exibicao = pd.DataFrame(produtos_paginados).copy()
        df_exibicao["Selecionar"] = False
        # df_exibicao["id_produto"] = df_exibicao["id_produto"].astype(str)

        # Colunas e Configuração
        cols_exibicao = ["Selecionar", "codigo", "descricao", "equipamento", "familia", "area_produtiva", "tempo_ciclo"]
        
        selecao = st.data_editor(
            df_exibicao[cols_exibicao].reset_index(drop=True),
            hide_index=True,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Selecionar", help="Marque para selecionar"),
                "codigo": st.column_config.TextColumn("Código"),
                "descricao": st.column_config.TextColumn("Descrição"),
                "equipamento": st.column_config.TextColumn("Equipamento"),
                "familia": st.column_config.TextColumn("Família"),
                "area_produtiva": st.column_config.TextColumn("Área Produtiva"),
                "tempo_ciclo": st.column_config.NumberColumn("Tempo de Ciclo", format="%.2f"),
            },
            key="grid_produtos"
        )

        # Lógica de Seleção
        selecionados = selecao[selecao["Selecionar"] == True]

        if len(selecionados) == 1:
            idx_paginado = selecionados.index[0]
            if idx_paginado < len(produtos_paginados):
                id_selecionado = produtos_paginados[idx_paginado].get("id")

                produto_completo = next((c for c in listar_todos_dados_produtos() if c.get("id") == id_selecionado), None)

                if produto_completo:
                    st.session_state.produto_selecionado = produto_completo
        elif len(selecionados) > 1:
            st.error("Selecione apenas 1 produto por vez.")
        else:
            st.session_state.produto_selecionado = None

    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    
    total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    if col_pag1.button("⬅️", disabled=st.session_state.pagina <= 0):
        st.session_state.pagina -= 1
        st.rerun()

    col_pag2.write(f"Página {st.session_state.pagina + 1} de {total_paginas}")

    if col_pag3.button("➡️", disabled=(st.session_state.pagina + 1) >= total_paginas):
        st.session_state.pagina += 1
        st.rerun()

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Listar"):
            st.session_state.aba = "Listar"
            st.rerun()
        if col2.button("Incluir"):
            st.session_state.aba = "Incluir"
            st.rerun()
        if col3.button("Alterar"):
            st.session_state.aba = "Alterar"
            st.rerun()
        if col4.button("Excluir"):
            st.session_state.aba = "Excluir"
elif st.session_state.aba == "Incluir":
    st.subheader("Incluir Produto")

    # Verifica se há cliente selecionado
    if st.session_state.cliente_selecionado is None:
        st.warning("Selecione um cliente antes de incluir um produto.")
        if st.button("Escolher cliente"):
            st.session_state.aba = "Listar"
            st.rerun()
    else:
        cliente = st.session_state.cliente_selecionado
        # Exibir via componente HTML para garantir que estilo seja aplicado
        html = f"""
        <style>
          .selected-client {{ color: orange !important; font-size:28px !important; font-weight:700 !important; margin:6px 0; }}
        </style>
        <div class="selected-client">Cliente selecionado: {cliente.get('empresa')}</div>
        """
        components.html(html, height=60)

        # Formulário aprimorado em colunas
        with st.form("form_incluir_produto"):
            col1, col2 = st.columns([2, 1])

            with col1:
                # Campo não editável com o cliente selecionado
                st.text_input("Cliente", value=cliente.get('empresa'), disabled=True)
                codigo = st.text_input("Código", max_chars=50)
                descricao = st.text_input("Descrição", max_chars=255)
                familia = st.text_input("Família")
                area_produtiva = st.text_input("Área Produtiva")
                area_embalagem = st.text_input("Área de Embalagem")

            with col2:
                lote_padrao = st.number_input("Lote Padrão", min_value=0.0, step=1.0, format="%f")
                area_rota = st.text_input("Área Rota")
                equipamento = st.text_input("Equipamento")
                classificacao = st.text_input("Classificação")
                tempo_ciclo = st.number_input("Tempo de Ciclo", min_value=0.0, step=0.1)

            # Botões lado-a-lado: Salvar e Sair sem Salvar
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar")
            with btn_col2:
                sair_sem_salvar = st.form_submit_button("Sair sem Salvar")

            if sair_sem_salvar:
                # Abandonar inclusão e voltar para seleção de cliente
                st.session_state.cliente_selecionado = None
                st.session_state.aba = "Listar"
                st.rerun()

            if salvar:
                novo_produto = {
                    "codigo": codigo,
                    "descricao": descricao,
                    "familia": familia,
                    "area_produtiva": area_produtiva,
                    "area_embalagem": area_embalagem,
                    "lote_padrao": lote_padrao,
                    "area_rota": area_rota,
                    "equipamento": equipamento,
                    "classificacao": classificacao,
                    "tempo_ciclo": tempo_ciclo,
                    "cliente_id": cliente.get("id") or cliente.get("id_cliente")
                }
                try:
                    incluir_produto(novo_produto)
                    st.success("Produto incluído com sucesso!")
                    # Limpar seleção de produto e voltar para listagem
                    st.session_state.produto_selecionado = None
                    st.session_state.aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao incluir produto: {e}")

elif st.session_state.aba == "Alterar":
    st.subheader("Alterar Produto")

    if st.session_state.produto_selecionado is None:
        st.warning("Selecione um produto na lista antes de alterar.")
        if st.button("Voltar para lista"):
            st.session_state.aba = "Listar"
            st.rerun()
    else:
        produto = st.session_state.produto_selecionado
        cliente = st.session_state.cliente_selecionado

        # Mostrar cliente não editável
        st.text_input("Cliente", value=cliente.get('empresa'), disabled=True)

        # Form para alterar
        with st.form("form_alterar_produto"):
            col1, col2 = st.columns([2, 1])
            with col1:
                codigo = st.text_input("Código", value=produto.get('codigo', ''), max_chars=50)
                descricao = st.text_input("Descrição", value=produto.get('descricao', ''), max_chars=255)
                familia = st.text_input("Família", value=produto.get('familia', ''))
                area_produtiva = st.text_input("Área Produtiva", value=produto.get('area_produtiva', ''))
                area_embalagem = st.text_input("Área de Embalagem", value=produto.get('area_embalagem', ''))
            with col2:
                lote_padrao = st.number_input("Lote Padrão", value=float(produto.get('lote_padrao') or 0.0), min_value=0.0, step=1.0, format="%f")
                area_rota = st.text_input("Área Rota", value=produto.get('area_rota', ''))
                equipamento = st.text_input("Equipamento", value=produto.get('equipamento', ''))
                classificacao = st.text_input("Classificação", value=produto.get('classificacao', ''))
                tempo_ciclo = st.number_input("Tempo de Ciclo", value=float(produto.get('tempo_ciclo') or 0.0), min_value=0.0, step=0.1)

            # Ações
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar Alterações")
            with btn_col2:
                cancelar = st.form_submit_button("Cancelar")

            if cancelar:
                st.session_state.produto_selecionado = None
                st.session_state.aba = "Listar"
                st.rerun()

            if salvar:
                dados = {
                    "codigo": codigo,
                    "descricao": descricao,
                    "familia": familia,
                    "area_produtiva": area_produtiva,
                    "area_embalagem": area_embalagem,
                    "lote_padrao": lote_padrao,
                    "area_rota": area_rota,
                    "equipamento": equipamento,
                    "classificacao": classificacao,
                    "tempo_ciclo": tempo_ciclo,
                    "cliente_id": cliente.get("id") or cliente.get("id_cliente")
                }
                try:
                    prod_id = produto.get('id')
                    alterar_produto(prod_id, dados)
                    st.success("Produto alterado com sucesso!")
                    st.session_state.produto_selecionado = None
                    st.session_state.aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao alterar produto: {e}")

elif st.session_state.aba == "Excluir":
    st.subheader("Excluir Produto")

    if st.session_state.produto_selecionado is None:
        st.warning("Selecione um produto na lista antes de excluir.")
        if st.button("Voltar para lista"):
            st.session_state.aba = "Listar"
            st.rerun()
    else:
        produto = st.session_state.produto_selecionado
        st.markdown(f"**Produto selecionado:** {produto.get('descricao')} ({produto.get('codigo')})")
        col_confirm, col_cancel = st.columns([1, 1])
        if col_cancel.button("Cancelar"):
            st.session_state.produto_selecionado = None
            st.session_state.aba = "Listar"
            st.rerun()
        if col_confirm.button("Confirmar Exclusão"):
            try:
                prod_id = produto.get('id')
                excluir_produto(prod_id)
                st.success("Produto excluído com sucesso")
                st.session_state.produto_selecionado = None
                st.session_state.aba = "Listar"
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao excluir produto: {e}")