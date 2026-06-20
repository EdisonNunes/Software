import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd

from pages.crud import supabase,  listar_clientes, listar_todos_dados_clientes, incluir_cliente,excluir_cliente, alterar_cliente
from components.sidebar import render_app_sidebar
from components.session_state import ensure_session_state

if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

render_app_sidebar()

st.info(f'### Clientes Cadastrados',icon=':material/factory:')

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

        # Definir colunas para exibição
        cols_exibicao = ["Selecionar", "empresa", "cidade", "telefone", "contato", "email"]

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
        if col4.button("Excluir", disabled=st.session_state.clientes_selecionado is None):
            st.session_state.clientes_aba = "Excluir"
            st.rerun()

elif st.session_state.clientes_aba == "Incluir":
    st.subheader("🏢 Incluir Novo Cliente")
    with st.form("form_incluir", clear_on_submit=False):
        st.markdown("### Dados da Empresa")
        col1, col2 = st.columns([3, 2])

        with col1:
            empresa = st.text_input("Empresa *").strip()

        with col2:
            cnpj = st.text_input("CNPJ").strip()

        st.markdown("### Endereço")

        col1, col2, col3 = st.columns([2, 4, 1])

        with col1:
            cep = st.text_input("CEP").strip()

        with col2:
            endereco = st.text_input("Endereço").strip()

        with col3:
            uf = st.text_input("UF").strip()

        col1, col2 = st.columns([3, 2])

        with col1:
            cidade = st.text_input("Cidade").strip()

        st.markdown("### Contato")

        col1, col2 = st.columns(2)

        with col1:
            contato = st.text_input("Contato").strip()

        with col2:
            telefone = st.text_input("Telefone").strip()

        email = st.text_input("Email").strip()

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
        }

        st.divider()

        col1, col2, col3 = st.columns([2, 1, 2])

        with col1:
            submitted = st.form_submit_button(
                "💾 Incluir Cliente",
                use_container_width=True
            )

        with col3:
            voltar_inc = st.form_submit_button(
                "↩️ Voltar",
                use_container_width=True
            )

        if submitted:
            try:
                incluir_cliente(dados)
                st.success("Cliente incluído com sucesso!")
            except ValueError as e:
                st.error(str(e))
            st.session_state.clientes_aba = "Listar"
            st.rerun()
        if voltar_inc:
                st.session_state.clientes_aba = "Listar"
                st.rerun()        

elif st.session_state.clientes_aba == "Alterar":
    st.subheader("✏️ Alterar Cliente")
    clientes = listar_todos_dados_clientes()
    cliente = st.session_state.clientes_selecionado or (clientes[0] if clientes else None)

    if cliente:
        with st.form("form_alterar"):
            st.markdown("### Dados da Empresa")
            col1, col2 = st.columns([3, 2])
            with col1:
                empresa = st.text_input(
                    "Empresa *",
                    value=cliente.get("empresa", "")
                )
            with col2:
                cnpj = st.text_input(
                    "CNPJ",
                    value=cliente.get("cnpj", "")
                )
            st.markdown("### Endereço")

            col1, col2, col3 = st.columns([2, 4, 1])

            with col1:
                cep = st.text_input(
                    "CEP",
                    value=cliente.get("cep", "")
                )

            with col2:
                endereco = st.text_input(
                    "Endereço",
                    value=cliente.get("endereco", "")
                )

            with col3:
                uf = st.text_input(
                    "UF",
                    value=cliente.get("uf", "")
                )

            col1, col2 = st.columns([3, 2])

            with col1:
                cidade = st.text_input(
                    "Cidade",
                    value=cliente.get("cidade", "")
                )

            st.markdown("### Contato")

            col1, col2 = st.columns(2)

            with col1:
                contato = st.text_input(
                    "Contato",
                    value=cliente.get("contato", "")
                )

            with col2:
                telefone = st.text_input(
                    "Telefone",
                    value=cliente.get("telefone", "")
                )

            email = st.text_input(
                "Email",
                value=cliente.get("email", "")
            )

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
            }

            st.divider()

            col1, col2, col3 = st.columns([2, 1, 2])

            with col1:
                submitted_alter = st.form_submit_button(
                    "💾 Salvar Alterações",
                    use_container_width=True
                )

            with col3:
                voltar_alter = st.form_submit_button(
                    "↩️ Voltar",
                    use_container_width=True
                )

            if submitted_alter:
                try:
                    alterar_cliente(cliente["id"], dados)
                    st.success("Cliente alterado com sucesso!")
                    st.session_state.clientes_aba = "Listar"
                    st.rerun()

                except ValueError as e:

                    st.error(str(e))

            if voltar_alter:
                st.session_state.clientes_aba = "Listar"
                st.rerun()        

elif st.session_state.clientes_aba == "Excluir":
    st.subheader("Excluir Cliente")
    clientes = listar_clientes()
    cliente = st.session_state.clientes_selecionado or (clientes[0] if clientes else None)

    if cliente:
        texto1 = "Deseja realmente excluir o cliente: "
        texto2 = f'{cliente['empresa']} 👉Filial : {cliente['cidade']}'
        st.success(f'##### :warning: ATENÇÃO !\n###### 👉 {texto1}\n###### 🟢 {texto2}')
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Excluir Cliente"):
                excluir_cliente(cliente["id"])
                st.success("Cliente excluído com sucesso!")
                st.session_state.clientes_selecionado = None
                st.session_state.clientes_aba = "Listar"
                st.rerun()
        with col2:
            if st.button("Voltar sem excluir"):
                st.session_state.clientes_aba = "Listar"
                st.rerun()


