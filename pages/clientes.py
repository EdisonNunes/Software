import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd

from pages.crud import supabase,  listar_clientes, listar_todos_dados_clientes, incluir_cliente, excluir_cliente, alterar_cliente, desativar_cliente, reativar_cliente
from components.sidebar import render_app_sidebar
from components.top_menu import render_top_menu
from components.session_state import ensure_session_state

if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

render_app_sidebar()
render_top_menu()

st.info(f'# Cadastro de Clientes', icon=':material/factory:')

# Inicializa session_state
ensure_session_state(
    {
        "clientes_aba": "Listar",
        "clientes_pagina": 0,
        "clientes_busca_empresa": "",
        "clientes_selecionado": None,
    }
)

PAGE_SIZE = 10

if st.session_state.clientes_aba == "Listar":
    #st.subheader("Lista de Clientes")
    busca_atual = st.text_input("Buscar por empresa", st.session_state.clientes_busca_empresa)
    if busca_atual != st.session_state.clientes_busca_empresa:
        st.session_state.clientes_busca_empresa = busca_atual
        st.session_state.clientes_pagina = 0
        st.rerun()

    clientes = listar_clientes(filtro_empresa=st.session_state.clientes_busca_empresa)

    total = len(clientes)
    total = 10
    inicio = st.session_state.clientes_pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE
    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

    if clientes:
        clientes_paginados = clientes[inicio:fim]
        df_exibicao = pd.DataFrame(clientes_paginados).copy()
        
        # Adicionar coluna de seleção com checkbox
        df_exibicao["Selecionar"] = False
        df_exibicao["id"] = df_exibicao["id"].astype(str)
        df_exibicao["situacao"] = df_exibicao["status"].apply(
            lambda v: "🟢 Ativa" if v else "🔴 Suspensa"
        )

        # Definir colunas para exibição
        cols_exibicao = ["Selecionar", "empresa", "cidade", "telefone", "contato", "email", "situacao"]

        # Configurar Grid
        selecao = st.data_editor(
            df_exibicao[cols_exibicao].reset_index(drop=True),
            hide_index=True,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Selecionar", help="Marque para selecionar"),
                "empresa": st.column_config.TextColumn("Empresa"),
                "cidade": st.column_config.TextColumn("Cidade"),
                "telefone": st.column_config.TextColumn("Telefone"),
                "contato": st.column_config.TextColumn("Contato"),
                "email": st.column_config.TextColumn("Email"),
                "situacao": st.column_config.TextColumn("Situação"),
            },
            key="clientes_grid_clientes"
        )

        # Lógica de Seleção
        selecionados = selecao[selecao["Selecionar"] == True]

        if len(selecionados) == 1:
            idx_paginado = selecionados.index[0]
            if idx_paginado < len(clientes_paginados):
                cliente_selecionado_pag = clientes_paginados[idx_paginado]
                id_selecionado = cliente_selecionado_pag["id"]

                cliente_completo = next((c for c in listar_todos_dados_clientes() if c["id"] == id_selecionado), None)
                if cliente_completo:
                    st.session_state.clientes_selecionado = cliente_completo
        elif len(selecionados) > 1:
            st.error("Selecione apenas 1 cliente por vez.")

    # Controles de Navegação (Estilo proposta.py)
    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    
    total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    # Ajuste para base 1 na visualização, mas mantendo base 0 no estado se preferir, 
    # ou migrando tudo para base 1.
    # O código original usava base 0 (inicio = st.session_state.clientes_pagina * PAGE_SIZE).
    # O código proposta.py usa base 1. 
    # Vamos manter base 0 no backend (session_state.pagina) para minimizar impacto no resto do código, 
    # mas exibir como Base 1.

    if col_pag1.button("⬅️", disabled=st.session_state.clientes_pagina <= 0):
        st.session_state.clientes_pagina -= 1
        st.rerun()

    col_pag2.write(f"Página {st.session_state.clientes_pagina + 1} de {total_paginas}")

    if col_pag3.button("➡️", disabled=(st.session_state.clientes_pagina + 1) >= total_paginas):
        st.session_state.clientes_pagina += 1
        st.rerun()

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Listar"):
            st.session_state.clientes_aba = "Listar"
            st.rerun()
        if col2.button("Incluir"):
            st.session_state.clientes_aba = "Incluir"
            st.rerun()
        if col3.button("Alterar", disabled=st.session_state.clientes_selecionado is None):
            st.session_state.clientes_aba = "Alterar"
            st.rerun()

        cliente_sel = st.session_state.clientes_selecionado
        if cliente_sel is None:
            col4.button("🔒 Suspender", disabled=True)
        elif cliente_sel.get("status", True):
            if col4.button("🔒 Suspender"):
                try:
                    desativar_cliente(cliente_sel.get("id"))
                    st.session_state.clientes_selecionado = None
                    st.success("Cliente suspenso com sucesso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao suspender cliente: {e}")
        else:
            if col4.button("🔓 Reativar"):
                try:
                    reativar_cliente(cliente_sel.get("id"))
                    st.session_state.clientes_selecionado = None
                    st.success("Cliente reativado com sucesso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao reativar cliente: {e}")

elif st.session_state.clientes_aba == "Incluir":
    st.subheader("Incluir Cliente")
    st.caption("Campos com * são obrigatórios.")

    with st.form("form_incluir_cliente", clear_on_submit=False):
        st.markdown("### Dados da Empresa")
        col1, col2 = st.columns([2, 1])
        with col1:
            empresa = st.text_input("Empresa *", max_chars=120).strip()
        with col2:
            cnpj = st.text_input("CNPJ", max_chars=20).strip()

        st.markdown("### Endereço")
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            cep = st.text_input("CEP", max_chars=12).strip()
        with col2:
            endereco = st.text_input("Endereço", max_chars=255).strip()
        with col3:
            uf = st.text_input("UF", max_chars=2).strip()

        col1, col2 = st.columns([2, 1])
        with col1:
            cidade = st.text_input("Cidade", max_chars=120).strip()

        st.markdown("### Contato")
        col1, col2 = st.columns(2)
        with col1:
            contato = st.text_input("Contato", max_chars=120).strip()
        with col2:
            telefone = st.text_input("Telefone", max_chars=20).strip()

        col1, col2 = st.columns([3, 1])
        with col1:
            email = st.text_input("Email", max_chars=120).strip()
        with col2:
            opcoes_status = ["Ativa", "Suspensa"]
            status_sel = st.selectbox("Situação", opcoes_status, index=0, width="stretch")

        dados = {
            "empresa": empresa,
            "cnpj": cnpj,
            "cep": cep,
            "endereco": endereco,
            "cidade": cidade,
            "uf": uf,
            "contato": contato,
            "telefone": telefone,
            "email": email,
            "status": (status_sel == "Ativa"),
        }

        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            salvar = st.form_submit_button("Salvar", width="stretch")
        with btn_col2:
            sair_sem_salvar = st.form_submit_button("Sair sem Salvar", width="stretch")

        if sair_sem_salvar:
            st.session_state.clientes_aba = "Listar"
            st.rerun()

        if salvar:
            try:
                incluir_cliente(dados)
                st.success("Cliente incluído com sucesso!")
                st.session_state.clientes_selecionado = None
                st.session_state.clientes_aba = "Listar"
                st.rerun()
            except ValueError as e:
                st.error(str(e))

elif st.session_state.clientes_aba == "Alterar":
    st.subheader("Alterar Cliente")
    cliente = st.session_state.clientes_selecionado

    if cliente is None:
        st.warning("Selecione um cliente na lista antes de alterar.")
        if st.button("Voltar para lista"):
            st.session_state.clientes_aba = "Listar"
            st.rerun()
    else:
        st.success(
            f"# Cliente selecionado   :point_right: {cliente.get('empresa')}",
            icon=':material/factory:',
        )

        with st.form("form_alterar_cliente"):
            st.markdown("### Dados da Empresa")
            col1, col2 = st.columns([2, 1])
            with col1:
                empresa = st.text_input(
                    "Empresa *",
                    value=cliente.get("empresa", ""),
                    max_chars=120,
                )
            with col2:
                cnpj = st.text_input(
                    "CNPJ",
                    value=cliente.get("cnpj", ""),
                    max_chars=20,
                )

            st.markdown("### Endereço")
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                cep = st.text_input(
                    "CEP",
                    value=cliente.get("cep", ""),
                    max_chars=12,
                )
            with col2:
                endereco = st.text_input(
                    "Endereço",
                    value=cliente.get("endereco", ""),
                    max_chars=255,
                )
            with col3:
                uf = st.text_input(
                    "UF",
                    value=cliente.get("uf", ""),
                    max_chars=2,
                )

            col1, col2 = st.columns([2, 1])
            with col1:
                cidade = st.text_input(
                    "Cidade",
                    value=cliente.get("cidade", ""),
                    max_chars=120,
                )

            st.markdown("### Contato")
            col1, col2 = st.columns(2)
            with col1:
                contato = st.text_input(
                    "Contato",
                    value=cliente.get("contato", ""),
                    max_chars=120,
                )
            with col2:
                telefone = st.text_input(
                    "Telefone",
                    value=cliente.get("telefone", ""),
                    max_chars=20,
                )

            col1, col2 = st.columns([3, 1])
            with col1:
                email = st.text_input(
                    "Email",
                    value=cliente.get("email", ""),
                    max_chars=120,
                )
            with col2:
                opcoes_status = ["Ativa", "Suspensa"]
                status_atual = cliente.get("status", True)
                status_idx = 0 if status_atual else 1
                status_sel = st.selectbox(
                    "Situação",
                    opcoes_status,
                    index=status_idx,
                    width="stretch",
                )

            dados = {
                "empresa": empresa.strip(),
                "cnpj": cnpj.strip(),
                "cep": cep.strip(),
                "endereco": endereco.strip(),
                "cidade": cidade.strip(),
                "uf": uf.strip(),
                "contato": contato.strip(),
                "telefone": telefone.strip(),
                "email": email.strip(),
                "status": (status_sel == "Ativa"),
            }

            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar", width="stretch")
            with btn_col2:
                cancelar = st.form_submit_button("Cancelar", width="stretch")

            if cancelar:
                st.session_state.clientes_selecionado = None
                st.session_state.clientes_aba = "Listar"
                st.rerun()

            if salvar:
                try:
                    alterar_cliente(cliente["id"], dados)
                    st.success("Cliente alterado com sucesso!")
                    st.session_state.clientes_selecionado = None
                    st.session_state.clientes_aba = "Listar"
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


