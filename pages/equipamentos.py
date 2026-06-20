# Admin e Supervisor veem tudo.
# Gerente e Funcionário veem apenas os Equipamentos da própria empresa

import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd
import streamlit.components.v1 as components

from pages.crud import listar_clientes
from pages.crud import (
    listar_equipamentos,
    listar_todos_dados_equipamentos,
    incluir_equipamento,
    alterar_equipamento,
    excluir_equipamento,
    listar_todos_dados_linhas,
    listar_todos_dados_procs,
)

from components.top_menu import render_top_menu
from components.sidebar import render_app_sidebar
from components.session_state import ensure_session_state

if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

render_app_sidebar()
    
render_top_menu()

st.info(f'# Cadastrados de Equipamentos',icon=':material/precision_manufacturing:')

ensure_session_state(
    {
        "equip_aba": "Listar",
        "equip_pagina": 0,
        "equip_busca_descricao": "",
        "equip_selecionada": None,
        "equip_cliente_selecionado": None,
        "equip_cliente_pagina": 0,
    }
)

if (st.session_state.get("role") not in ["admin", "supervisor"]):
   if ( st.session_state.equip_cliente_selecionado is None and st.session_state.get("cliente")):
        st.session_state.equip_cliente_selecionado = (st.session_state.cliente)

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
                    key="equipamentos_grid_clientes"
                )

                selecionados_cli = selecao_cli[selecao_cli["Selecionar"] == True]

                if len(selecionados_cli) == 1:
                    idx = selecionados_cli.index[0]
                    if idx < len(clientes_paginados):
                        st.session_state.equip_cliente_selecionado = (clientes_paginados[idx])
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
        else:
            if st.session_state.get("cliente"):
                st.session_state.equip_cliente_selecionado = (st.session_state.cliente)
                st.rerun()
            else:
                st.error("Empresa do usuário não encontrada.")
                st.stop()

    # Se chegou aqui, há um cliente selecionado: mostrar Equipamentos apenas deste cliente
    cliente = st.session_state.equip_cliente_selecionado
    if cliente and st.session_state.get("role") in ["admin", "supervisor"]:
        st.success(f"# Equipamentos da empresa   :point_right: {cliente.get('empresa')}",icon=':material/precision_manufacturing:')

        if st.button("Limpar seleção de cliente"):
            st.session_state.equip_cliente_selecionado = None
            st.rerun()

    if cliente:
        equipamentos = listar_equipamentos(cliente.get('id') or cliente.get('id_cliente'))
    else:
        equipamentos = []   
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
            key="equipamentos_grid_equipamentos"
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
        if col3.button("Alterar", disabled=st.session_state.equip_selecionada is None):
            st.session_state.equip_aba = "Alterar"
            st.rerun()
        if col4.button("Excluir", disabled=st.session_state.equip_selecionada is None):
            st.session_state.equip_aba = "Excluir"
            st.rerun()
            
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
        cliente_id = cliente.get("id") or cliente.get("id_cliente")
        linhas = listar_todos_dados_linhas(cliente_id)
        processos = listar_todos_dados_procs(cliente_id)

        if not linhas:
            st.warning("Cadastre ao menos uma linha antes de incluir equipamento.")
            if st.button("Ir para módulo de Linhas"):
                st.switch_page("pages/linhas.py")
            st.stop()

        if not processos:
            st.warning("Cadastre ao menos um processo antes de incluir equipamento.")
            if st.button("Ir para módulo de Processos"):
                st.switch_page("pages/processos.py")
            st.stop()

        linha_por_id = {
            item.get("id"): item.get("descricao", "")
            for item in linhas
            if item.get("id")
        }
        processo_por_id = {
            item.get("id"): item.get("descricao", "")
            for item in processos
            if item.get("id")
        }
        opcoes_linha = list(linha_por_id.keys())
        opcoes_processo = list(processo_por_id.keys())
        unidades_capac = ["kg", "litros", "unidades"]
        unidades_tempo = ["min", "horas", "dia", "mes"]

        # Exibir via componente HTML para garantir que estilo seja aplicado
        html = f"""
        <style>
          .selected-client {{ color: orange !important; font-size:28px !important; font-weight:700 !important; margin:6px 0; }}
        </style>
        <div class="selected-client">Cliente selecionado: {cliente.get('empresa')}</div>
        """
        components.html(html, height=60)

        with st.form("form_incluir_equipamento"):
            st.markdown("#### Identificação")
            col_id_1, col_id_2 = st.columns(2)
            with col_id_1:
                codigo = st.text_input("Código", max_chars=50, placeholder="Ex.: EQP-001")
            with col_id_2:
                classif = st.selectbox("Classificação", ["Principal", "Secundário"], width="stretch")

            descricao = st.text_input("Descrição", max_chars=255, placeholder="Nome descritivo do equipamento")

            st.markdown("#### Estrutura")
            col_estr_1, col_estr_2 = st.columns(2)
            with col_estr_1:
                linha_id = st.selectbox(
                    "Linha",
                    options=opcoes_linha,
                    format_func=lambda item_id: linha_por_id.get(item_id, ""),
                    width="stretch",
                )
            with col_estr_2:
                processo_id = st.selectbox(
                    "Processo",
                    options=opcoes_processo,
                    format_func=lambda item_id: processo_por_id.get(item_id, ""),
                    width="stretch",
                )

            st.markdown("#### Capacidade")
            col_cap_1, col_cap_2, col_cap_3 = st.columns([2, 1, 1])
            with col_cap_1:
                capacidade = st.number_input("Capacidade", min_value=0.0, step=0.1, format="%.2f")
            with col_cap_2:
                unidade_capac = st.selectbox("Unidade", options=unidades_capac, width="stretch")
            with col_cap_3:
                unidade_tempo = st.selectbox("Tempo", options=unidades_tempo, width="stretch")

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
                try:
                    incluir_equipamento(
                        codigo=codigo,
                        descricao=descricao,
                        classif=classif,
                        linha=linha_id,
                        processo=processo_id,
                        capacidade=capacidade,
                        unidade_capac=unidade_capac,
                        unidade_tempo=unidade_tempo,
                        cliente_id=cliente_id,
                    )
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
        cliente_id = cliente.get("id") or cliente.get("id_cliente")
        linhas = listar_todos_dados_linhas(cliente_id)
        processos = listar_todos_dados_procs(cliente_id)

        if not linhas or not processos:
            st.warning("Para editar, é necessário ter ao menos uma linha e um processo cadastrados.")
            if st.button("Voltar para lista"):
                st.session_state.equip_aba = "Listar"
                st.rerun()
            st.stop()

        linha_por_id = {
            item.get("id"): item.get("descricao", "")
            for item in linhas
            if item.get("id")
        }
        processo_por_id = {
            item.get("id"): item.get("descricao", "")
            for item in processos
            if item.get("id")
        }
        opcoes_linha = list(linha_por_id.keys())
        opcoes_processo = list(processo_por_id.keys())
        unidades_capac = ["kg", "litros", "unidades"]
        unidades_tempo = ["min", "horas", "dia", "mes"]

        linha_id_atual = equipamento.get("linha")
        processo_id_atual = equipamento.get("processo")
        if linha_id_atual not in opcoes_linha:
            linha_id_atual = opcoes_linha[0]
        if processo_id_atual not in opcoes_processo:
            processo_id_atual = opcoes_processo[0]

        unidade_capac_atual = equipamento.get("unidade_capac") if equipamento.get("unidade_capac") in unidades_capac else unidades_capac[0]
        unidade_tempo_atual = equipamento.get("unidade_tempo") if equipamento.get("unidade_tempo") in unidades_tempo else unidades_tempo[0]
        classif_atual = equipamento.get("classif") if equipamento.get("classif") in ["Principal", "Secundário"] else "Principal"

        # Mostrar cliente não editável
        st.text_input("Cliente", value=cliente.get('empresa'), disabled=True)

        # Form para alterar
        with st.form("form_alterar_equipamento"):
            st.markdown("#### Identificação")
            col_id_1, col_id_2 = st.columns(2)
            with col_id_1:
                codigo = st.text_input("Código", value=equipamento.get('codigo', ''), max_chars=50)
            with col_id_2:
                classif = st.selectbox(
                    "Classificação",
                    ["Principal", "Secundário"],
                    index=0 if classif_atual == "Principal" else 1,
                    width="stretch",
                )

            descricao = st.text_input("Descrição", value=equipamento.get('descricao', ''), max_chars=255)

            st.markdown("#### Estrutura")
            col_estr_1, col_estr_2 = st.columns(2)
            with col_estr_1:
                linha_id = st.selectbox(
                    "Linha",
                    options=opcoes_linha,
                    index=opcoes_linha.index(linha_id_atual),
                    format_func=lambda item_id: linha_por_id.get(item_id, ""),
                    width="stretch",
                )
            with col_estr_2:
                processo_id = st.selectbox(
                    "Processo",
                    options=opcoes_processo,
                    index=opcoes_processo.index(processo_id_atual),
                    format_func=lambda item_id: processo_por_id.get(item_id, ""),
                    width="stretch",
                )

            st.markdown("#### Capacidade")
            col_cap_1, col_cap_2, col_cap_3 = st.columns([2, 1, 1])
            with col_cap_1:
                capacidade = st.number_input(
                    "Capacidade",
                    min_value=0.0,
                    value=float(equipamento.get("capacidade") or 0.0),
                    step=0.1,
                    format="%.2f",
                )
            with col_cap_2:
                unidade_capac = st.selectbox(
                    "Unidade",
                    options=unidades_capac,
                    index=unidades_capac.index(unidade_capac_atual),
                    width="stretch",
                )
            with col_cap_3:
                unidade_tempo = st.selectbox(
                    "Tempo",
                    options=unidades_tempo,
                    index=unidades_tempo.index(unidade_tempo_atual),
                    width="stretch",
                )

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
                try:
                    equip_id = equipamento.get('id')
                    alterar_equipamento(
                        equipamento_id=equip_id,
                        codigo=codigo,
                        classif=classif,
                        descricao=descricao,
                        linha=linha_id,
                        processo=processo_id,
                        capacidade=capacidade,
                        unidade_capac=unidade_capac,
                        unidade_tempo=unidade_tempo,
                    )
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


