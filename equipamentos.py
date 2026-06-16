# Admin e Supervisor veem tudo.
# Gerente e Funcionário veem apenas os Equipamentos da própria empresa

import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd
import streamlit.components.v1 as components

from crud import listar_clientes, listar_todos_dados_clientes
from crud import listar_equipamentos, listar_todos_dados_equipamentos, incluir_equipamento, alterar_equipamento, excluir_equipamento
st.info(f'# Cadastrados de Equipamentos',icon=':material/precision_manufacturing:')

if "equip_aba" not in st.session_state:
    st.session_state.equip_aba = "Listar"

if "equip_pagina" not in st.session_state:
    st.session_state.equip_pagina = 0

if "equip_busca_descricao" not in st.session_state:
    st.session_state.equip_busca_descricao = ""

if "equip_selecionada" not in st.session_state:
    st.session_state.equip_selecionada = None

if "equip_cliente_selecionado" not in st.session_state:
    st.session_state.equip_cliente_selecionado = None

if "equip_cliente_pagina" not in st.session_state:
    st.session_state.equip_cliente_pagina = 0


PAGE_SIZE = 10

if st.session_state.equip_aba == "Listar":
    # Se nenhum cliente selecionado, primeiro mostrar grid de clientes
    busca_atual = st.text_input("Buscar Equipamento", st.session_state.equip_busca_descricao)
    if busca_atual != st.session_state.equip_busca_descricao:
        st.session_state.equip_busca_descricao = busca_atual
        st.session_state.equip_cliente_pagina = 0
        st.session_state.equip_pagina = 0
        st.rerun()

    if st.session_state.equip_cliente_selecionado is None:
        # Admin e Supervisor escolhem a empresa
        print("Role do usuário:", st.session_state.get("role"))
        if st.session_state.get("role") in ["admin", "supervisor"]:
            clientes = listar_clientes(filtro_empresa=st.session_state.equip_busca_descricao)

            total = len(clientes)
            inicio = st.session_state.equip_cliente_pagina * PAGE_SIZE
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
                            st.session_state.equip_cliente_selecionado = cliente_completo
                            st.session_state.equip_pagina = 0
                            st.rerun()
                elif len(selecionados_cli) > 1:
                    st.error("Selecione apenas 1 cliente por vez.")

            # Paginação de clientes
            col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
            total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            if col_pag1.button("⬅️", disabled=st.session_state.equip_cliente_pagina <= 0):
                st.session_state.equip_cliente_pagina -= 1
                st.rerun()
            col_pag2.write(f"Página {st.session_state.equip_cliente_pagina + 1} de {total_paginas}")
            if col_pag3.button("➡️", disabled=(st.session_state.equip_cliente_pagina + 1) >= total_paginas):
                st.session_state.equip_cliente_pagina += 1
                st.rerun()

            # Não mostrar botões de ação antes da seleção do cliente
            st.stop()
        # Gerente e Funcionário usam automaticamente sua empresa
        else:
            cliente_completo = next((c for c in listar_todos_dados_clientes()
                    if c.get("id") == st.session_state.get("cliente_id")), None)
            if cliente_completo:
                st.session_state.equip_cliente_selecionado = (cliente_completo)
                st.rerun()

    # Se chegou aqui, há um cliente selecionado: mostrar Equipamentos apenas deste cliente
    cliente = st.session_state.equip_cliente_selecionado
    if cliente and st.session_state.get("role") in ["admin", "supervisor"]:
        st.success(f"# Equipamentos da empresa   :point_right: {cliente.get('empresa')}",icon=':material/precision_manufacturing:')

        if st.button("Limpar seleção de cliente"):
            st.session_state.equip_cliente_selecionado = None
            st.rerun()
        # # print("ID do cliente selecionado para filtro de Equipamentos:", cliente.get('id') or cliente.get('id_cliente'))
        # # print("Cliente selecionado (completo):", cliente)
    
    equipamentos = listar_equipamentos(cliente.get('id') or cliente.get('id_cliente'))
    total = len(equipamentos)
    inicio = st.session_state.equip_pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE
    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

    if equipamentos:
        equipamentos_paginados = equipamentos[inicio:fim]
        df_exibicao = pd.DataFrame(equipamentos_paginados).copy()
        df_exibicao["Selecionar"] = False
        # df_exibicao["id_produto"] = df_exibicao["id_produto"].astype(str)

        # Colunas e Configuração
        cols_exibicao = ["Selecionar", "codigo", "descricao", "classif"]
        
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
                  "classif": st.column_config.TextColumn(
                    "Classificação"
                ),
            },
            key="grid_equipamentos"
        )

        # Lógica de Seleção
        selecionados = selecao[selecao["Selecionar"] == True]

        if len(selecionados) == 1:
            idx_paginado = selecionados.index[0]
            if idx_paginado < len(equipamentos_paginados):
                id_selecionado = equipamentos_paginados[idx_paginado].get("id")

                equip_completo = next((c for c in listar_todos_dados_equipamentos() if c.get("id") == id_selecionado), None)

                if equip_completo:
                    st.session_state.equip_selecionada = equip_completo
        elif len(selecionados) > 1:
            st.error("Selecione apenas 1 equipamento por vez.")
        else:
            st.session_state.equip_selecionada = None

    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    
    total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    if col_pag1.button("⬅️", disabled=st.session_state.equip_pagina <= 0):
        st.session_state.equip_pagina -= 1
        st.rerun()

    col_pag2.write(f"Página {st.session_state.equip_pagina + 1} de {total_paginas}")

    if col_pag3.button("➡️", disabled=(st.session_state.equip_pagina + 1) >= total_paginas):
        st.session_state.equip_pagina += 1
        st.rerun()

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Listar"):
            st.session_state.equip_aba = "Listar"
            st.rerun()
        if col2.button("Incluir"):
            st.session_state.equip_aba = "Incluir"
            st.rerun()
        if col3.button("Alterar"):
            st.session_state.equip_aba = "Alterar"
            st.rerun()
        if col4.button("Excluir"):
            st.session_state.equip_aba = "Excluir"
elif st.session_state.equip_aba == "Incluir":
    st.subheader("Incluir Equipamento")

    # Verifica se há cliente selecionado
    if st.session_state.equip_cliente_selecionado is None:
        st.warning("Selecione um cliente antes de incluir um produto.")
        if st.button("Escolher cliente"):
            st.session_state.equip_aba = "Listar"
            st.rerun()
    else:
        cliente = st.session_state.equip_cliente_selecionado
        # Exibir via componente HTML para garantir que estilo seja aplicado
        html = f"""
        <style>
          .selected-client {{ color: orange !important; font-size:28px !important; font-weight:700 !important; margin:6px 0; }}
        </style>
        <div class="selected-client">Cliente selecionado: {cliente.get('empresa')}</div>
        """
        components.html(html, height=60)

        # Formulário aprimorado em colunas
        with st.form("form_incluir_equipamento"):
            # Campo não editável com o cliente selecionado
            # st.text_input("Cliente", value=cliente.get('empresa'), disabled=True)
            codigo = st.text_input("Código", max_chars=50)
            descricao = st.text_input("Descrição", max_chars=255)
            classif = st.selectbox("Classificação", ["Principal", "Secundário"], width=200)

           # Botões lado-a-lado: Salvar e Sair sem Salvar
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar")
            with btn_col2:
                sair_sem_salvar = st.form_submit_button("Sair sem Salvar")

            if sair_sem_salvar:
                # Abandonar inclusão e voltar para seleção de cliente
                st.session_state.equip_cliente_selecionado = None
                st.session_state.equip_aba = "Listar"
                st.rerun()

            if salvar:
                cliente_id = (
                                cliente.get("id")
                                or cliente.get("id_cliente"))

                try:
                    incluir_equipamento(codigo, descricao, classif, cliente_id)
                    st.success("Equipamento incluído com sucesso!")
                    # Limpar seleção de equipamentos e voltar para listagem
                    st.session_state.equip_selecionada = None
                    st.session_state.equip_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao incluir equipamento: {e}")

elif st.session_state.equip_aba == "Alterar":
    st.subheader("Alterar Equipamento")

    if st.session_state.equip_selecionada is None:
        st.warning("Selecione um Equipamento na lista antes de alterar.")
        if st.button("Voltar para lista"):
            st.session_state.equip_aba = "Listar"
            st.rerun()
    else:
        equipamento = st.session_state.equip_selecionada
        cliente = st.session_state.equip_cliente_selecionado

        # Mostrar cliente não editável
        st.text_input("Cliente", value=cliente.get('empresa'), disabled=True)

        # Form para alterar
        with st.form("form_alterar_equipamento"):
            col1, col2 = st.columns([2, 1])
            with col1:
                codigo = st.text_input("Código", value=equipamento.get('codigo', ''), max_chars=50)
                descricao = st.text_input("Descrição", value=equipamento.get('descricao', ''), max_chars=255)
                classif = st.selectbox("Classificação", ["Principal", "Secundário"], index=0 if equipamento.get('classif') == "Principal" else 1, width=200)
                # Ações
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar Alterações")
            with btn_col2:
                cancelar = st.form_submit_button("Cancelar")

            if cancelar:
                st.session_state.equip_selecionada = None
                st.session_state.equip_aba = "Listar"
                st.rerun()

            if salvar:
                cliente_id = (
                    cliente.get("id")
                    or cliente.get("id_cliente")
                )

                try:
                    equip_id = equipamento.get('id')
                    alterar_equipamento(equip_id, codigo, classif, descricao)
                    st.success("Equipamento alterado com sucesso!")
                    st.session_state.equip_selecionada = None
                    st.session_state.equip_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao alterar Equipamento: {e}")

elif st.session_state.equip_aba == "Excluir":
    st.subheader("Excluir Equipamento")

    if st.session_state.equip_selecionada is None:
        st.warning("Selecione um Equipamento na lista antes de excluir.")
        if st.button("Voltar para lista"):
            st.session_state.equip_aba = "Listar"
            st.rerun()
    else:
        equip = st.session_state.equip_selecionada
        st.markdown(f"**Equipamento selecionado:** {equip.get('descricao')} ({equip.get('codigo')})")
        col_confirm, col_cancel = st.columns([1, 1])
        if col_cancel.button("Cancelar"):
            st.session_state.equip_selecionada = None
            st.session_state.equip_aba = "Listar"
            st.rerun()

        if col_confirm.button("Confirmar Exclusão ?"):
            try:
                equip_id = equip.get("id")
                excluir_equipamento(equip_id)
                st.success("Equipamento excluído com sucesso")
                st.session_state.equip_selecionada = None
                st.session_state.equip_aba = "Listar"
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao excluir Equipamento: {e}")
