# Admin e Supervisor veem tudo.
# Gerente e Funcionário veem apenas os Equipamentos da própria empresa

import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd

from pages.theme import read_streamlit_theme
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


def _hex_to_rgb(color_hex: str, fallback: tuple[int, int, int]) -> tuple[int, int, int]:
	valor = (color_hex or "").strip().lstrip("#")
	if len(valor) == 3:
		valor = "".join([c * 2 for c in valor])
	if len(valor) != 6:
		return fallback
	try:
		return int(valor[0:2], 16), int(valor[2:4], 16), int(valor[4:6], 16)
	except ValueError:
		return fallback


def _misturar(rgb_a: tuple[int, int, int], rgb_b: tuple[int, int, int], peso_a: float) -> tuple[int, int, int]:
	peso_a = max(0.0, min(1.0, peso_a))
	peso_b = 1.0 - peso_a
	return (
		int(rgb_a[0] * peso_a + rgb_b[0] * peso_b),
		int(rgb_a[1] * peso_a + rgb_b[1] * peso_b),
		int(rgb_a[2] * peso_a + rgb_b[2] * peso_b),
	)


def _contraste_texto(rgb: tuple[int, int, int]) -> str:
	brilho = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
	return "#0F172A" if brilho > 135 else "#F8FAFC"


def _banner_palette() -> dict[str, str]:
	tema = read_streamlit_theme()
	base = (tema.get("base") or "dark").lower()

	bg_rgb = _hex_to_rgb(
		tema.get("backgroundColor", "#FFFFFF" if base == "light" else "#0F172A"),
		(255, 255, 255) if base == "light" else (15, 23, 42),
	)
	sec_rgb = _hex_to_rgb(
		tema.get("secondaryBackgroundColor", "#F1F5F9" if base == "light" else "#1E293B"),
		(241, 245, 249) if base == "light" else (30, 41, 59),
	)
	pri_rgb = _hex_to_rgb(
		tema.get("primaryColor", "#2563EB"),
		(37, 99, 235),
	)
	text_rgb = _hex_to_rgb(
		tema.get("textColor", "#0F172A" if base == "light" else "#E2E8F0"),
		(15, 23, 42) if base == "light" else (226, 232, 240),
	)

	banner_bg = _misturar(sec_rgb, bg_rgb, 0.62)
	banner_border = _misturar(pri_rgb, sec_rgb, 0.58)
	title_color = _contraste_texto(banner_bg)
	body_color = "rgb({},{},{})".format(*_misturar(text_rgb, bg_rgb, 0.78))
	label_color = "rgb({},{},{})".format(*_misturar(pri_rgb, text_rgb, 0.60))

	return {
		"banner_bg": f"rgb({banner_bg[0]},{banner_bg[1]},{banner_bg[2]})",
		"banner_bg_soft": f"rgba({sec_rgb[0]},{sec_rgb[1]},{sec_rgb[2]},0.92)",
		"banner_border": f"rgb({banner_border[0]},{banner_border[1]},{banner_border[2]})",
		"title_color": title_color,
		"body_color": body_color,
		"label_color": label_color,
	}


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

        paleta = _banner_palette()
        st.markdown(
            f"""
            <div style="
                border: 1px solid {paleta['banner_border']};
                background: linear-gradient(135deg, {paleta['banner_bg']}, {paleta['banner_bg_soft']});
                border-radius: 18px;
                padding: 18px 20px;
                margin: 0.25rem 0 1rem 0;
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.18);
            ">
                <div style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: {paleta['label_color']}; font-weight: 800;">
                    Cliente selecionado
                </div>
                <div style="font-size: 1.45rem; font-weight: 800; color: {paleta['title_color']}; margin-top: 0.15rem;">
                    {cliente.get('empresa', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("form_incluir_equipamento"):
            st.markdown("#### Identificação")
            col_id_1, col_id_2 = st.columns(2)
            with col_id_1:
                codigo = st.text_input("Código", max_chars=50, placeholder="Ex.: EQP-001")
            with col_id_2:
                classif = st.selectbox("Classificação", ["Principal", "Secundário"])

            descricao = st.text_input("Descrição", max_chars=255, placeholder="Nome descritivo do equipamento")

            st.markdown("#### Estrutura")
            col_estr_1, col_estr_2 = st.columns(2)
            with col_estr_1:
                linha_id = st.selectbox(
                    "Linha",
                    options=opcoes_linha,
                    format_func=lambda item_id: linha_por_id.get(item_id, ""),
                )
            with col_estr_2:
                processo_id = st.selectbox(
                    "Processo",
                    options=opcoes_processo,
                    format_func=lambda item_id: processo_por_id.get(item_id, ""),
                )

            st.markdown("#### Capacidade")
            col_cap_1, col_cap_2, col_cap_3 = st.columns([2, 1, 1])
            with col_cap_1:
                capacidade = st.number_input("Capacidade", min_value=0.0, step=0.1, format="%.2f")
            with col_cap_2:
                unidade_capac = st.selectbox("Unidade", options=unidades_capac)
            with col_cap_3:
                unidade_tempo = st.selectbox("Tempo", options=unidades_tempo)

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
                )
            with col_estr_2:
                processo_id = st.selectbox(
                    "Processo",
                    options=opcoes_processo,
                    index=opcoes_processo.index(processo_id_atual),
                    format_func=lambda item_id: processo_por_id.get(item_id, ""),
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
                )
            with col_cap_3:
                unidade_tempo = st.selectbox(
                    "Tempo",
                    options=unidades_tempo,
                    index=unidades_tempo.index(unidade_tempo_atual),
                )

            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar")
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


