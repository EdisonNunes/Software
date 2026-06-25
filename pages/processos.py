# Admin e Supervisor veem tudo.
# Gerente e Funcionário veem apenas as áreas da própria empresa

import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client, Client
import os
import pandas as pd

from pages.theme import read_streamlit_theme
from pages.crud import listar_clientes
from pages.crud import listar_procs, listar_todos_dados_procs, incluir_proc, alterar_proc, excluir_proc

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


def _render_cliente_banner(cliente: dict, total_registros: int) -> None:
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
            <div style="display:flex; gap:18px; flex-wrap:wrap; margin-top:0.65rem; color:{paleta['body_color']}; font-size:0.95rem; font-weight:600;">
                <span><strong>Cidade:</strong> {cliente.get('cidade', '-') or '-'}</span>
                <span><strong>Registros:</strong> {total_registros}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

render_app_sidebar()
    
render_top_menu()

st.info(f'# Cadastro de Processos',icon=':material/activity_zone:')

ensure_session_state(
    {
        "proc_aba": "Listar",
        "proc_pagina": 0,
        "proc_busca_descricao": "",
        "proc_selecionada": None,
        "proc_cliente_selecionado": None,
        "proc_cliente_pagina": 0,
    }
)

if (st.session_state.get("role") not in ["admin", "supervisor"]):
   if (st.session_state.proc_cliente_selecionado is None and st.session_state.get("cliente")):
        st.session_state.proc_cliente_selecionado = st.session_state.cliente

PAGE_SIZE = 10

if st.session_state.proc_aba == "Listar":
    # Se nenhum cliente selecionado, primeiro mostrar grid de clientes
    if st.session_state.get("role") in ["admin", "supervisor"]:
        busca_atual = st.text_input("Buscar cliente", st.session_state.proc_busca_descricao)
        if busca_atual != st.session_state.proc_busca_descricao:
            st.session_state.proc_busca_descricao = busca_atual
            st.session_state.proc_cliente_pagina = 0
            st.session_state.proc_pagina = 0
            st.rerun()

    if st.session_state.proc_cliente_selecionado is None: 
        # Admin e Supervisor escolhem a empresa
        if st.session_state.get("role") in ["admin", "supervisor"]:                                       
            clientes = listar_clientes(filtro_empresa=st.session_state.proc_busca_descricao)
            total = len(clientes)
            inicio = st.session_state.proc_cliente_pagina * PAGE_SIZE
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
                    key="processos_grid_clientes"
                )

                selecionados_cli = selecao_cli[selecao_cli["Selecionar"] == True]

                if len(selecionados_cli) == 1:
                    idx = selecionados_cli.index[0]
                    if idx < len(clientes_paginados):
                        st.session_state.proc_cliente_selecionado = (clientes_paginados[idx])
                        st.session_state.proc_pagina = 0
                        st.rerun()
                elif len(selecionados_cli) > 1:
                    st.error("Selecione apenas 1 cliente por vez.")

            # Paginação de clientes
            col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
            total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            if col_pag1.button("⬅️", disabled=st.session_state.proc_cliente_pagina <= 0):
                st.session_state.proc_cliente_pagina -= 1
                st.rerun()
            col_pag2.write(f"Página {st.session_state.proc_cliente_pagina + 1} de {total_paginas}")
            if col_pag3.button("➡️", disabled=(st.session_state.proc_cliente_pagina + 1) >= total_paginas):
                st.session_state.proc_cliente_pagina += 1
                st.rerun()

            # Não mostrar botões de ação antes da seleção do cliente
            st.stop()
        else:
            # Gerente e Funcionário usam automaticamente sua empresa
            if st.session_state.get("cliente"):
                st.session_state.proc_cliente_selecionado = (st.session_state.cliente)
                st.rerun()
            else:
                st.error("Empresa do usuário não encontrada.")
                st.stop()

    # Se chegou aqui, há um cliente selecionado: mostrar Áreas apenas deste cliente
    cliente = st.session_state.proc_cliente_selecionado

    if cliente:
        procs = listar_procs(cliente.get('id') or cliente.get('id_cliente'))
    else:
        procs = []

    if cliente and st.session_state.get("role") in ["admin", "supervisor"]:
        _render_cliente_banner(cliente, len(procs))
        if st.button("Limpar seleção de cliente"):
            st.session_state.proc_cliente_selecionado = None
            st.rerun()
        
    total = len(procs)
    inicio = st.session_state.proc_pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE
    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

    if procs:
        procs_paginados = procs[inicio:fim]
        df_exibicao = pd.DataFrame(procs_paginados).copy()
        df_exibicao["Selecionar"] = False
        # df_exibicao["id_produto"] = df_exibicao["id_produto"].astype(str)

        # Colunas e Configuração
        cols_exibicao = ["Selecionar", "codigo", "descricao"]
        
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
                    "Nome"
                ),
            },
            key="processos_grid_procs",
        )

        # Lógica de Seleção
        selecionados = selecao[selecao["Selecionar"] == True]

        if len(selecionados) == 1:
            idx_paginado = selecionados.index[0]
            if idx_paginado < len(procs_paginados):
                id_selecionado = procs_paginados[idx_paginado].get("id")

                proc_completa = next((c for c in listar_todos_dados_procs() if c.get("id") == id_selecionado), None)

                if proc_completa:
                    st.session_state.proc_selecionada = proc_completa
        elif len(selecionados) > 1:
            st.error("Selecione apenas 1 área por vez.")

    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    
    total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    if col_pag1.button("⬅️", disabled=st.session_state.proc_pagina <= 0):
        st.session_state.proc_pagina -= 1
        st.rerun()

    col_pag2.write(f"Página {st.session_state.proc_pagina + 1} de {total_paginas}")

    if col_pag3.button("➡️", disabled=(st.session_state.proc_pagina + 1) >= total_paginas):
        st.session_state.proc_pagina += 1
        st.rerun()

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Listar"):
            st.session_state.proc_aba = "Listar"
            st.rerun()
        if col2.button("Incluir"):
            st.session_state.proc_aba = "Incluir"
            st.rerun()
        if col3.button("Alterar", disabled=st.session_state.proc_selecionada is None):
            st.session_state.proc_aba = "Alterar"
            st.rerun()
        if col4.button("Excluir", disabled=st.session_state.proc_selecionada is None):
            st.session_state.proc_aba = "Excluir"
            st.rerun()
            
elif st.session_state.proc_aba == "Incluir":
    st.subheader("Incluir Processo")

    # Verifica se há cliente selecionado
    if st.session_state.proc_cliente_selecionado is None:
        st.warning("Selecione um cliente antes de incluir um produto.")
        if st.button("Escolher cliente"):
            st.session_state.proc_aba = "Listar"
            st.rerun()
    else:
        cliente = st.session_state.proc_cliente_selecionado
        # Exibir via componente HTML para garantir que estilo seja aplicado
        html = f"""
        <style>
          .selected-client {{ color: orange !important; font-size:28px !important; font-weight:700 !important; margin:6px 0; }}
        </style>
        <div class="selected-client">{cliente.get('empresa')}</div>
        """
        components.html(html, height=60)

        # Formulário aprimorado em colunas
        with st.form("form_incluir_proc"):
            # Campo não editável com o cliente selecionado
            # st.text_input("Cliente", value=cliente.get('empresa'), disabled=True)
            codigo = st.text_input("Código / Identificação", max_chars=50)
            descricao = st.text_input("Nome do Processo", max_chars=255)

           # Botões lado-a-lado: Salvar e Sair sem Salvar
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar")
            with btn_col2:
                sair_sem_salvar = st.form_submit_button("Sair sem Salvar")

            if sair_sem_salvar:
                # Abandonar inclusão e voltar para seleção de cliente
                st.session_state.proc_cliente_selecionado = None
                st.session_state.proc_aba = "Listar"
                st.rerun()

            if salvar:
                cliente_id = (
                                cliente.get("id")
                                or cliente.get("id_cliente")
)
                try:
                    incluir_proc(codigo, descricao, cliente_id)
                    st.success("Processo incluído com sucesso!")
                    # Limpar seleção de processo e voltar para listagem
                    st.session_state.proc_selecionada = None
                    st.session_state.proc_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao incluir processo: {e}")

elif st.session_state.proc_aba == "Alterar":
    st.subheader("Alterar Processo")

    if st.session_state.proc_selecionada is None:
        st.warning("Selecione um processo na lista antes de alterar.")
        if st.button("Voltar para lista"):
            st.session_state.proc_aba = "Listar"
            st.rerun()
    else:
        proc = st.session_state.proc_selecionada
        cliente = st.session_state.proc_cliente_selecionado

        # Mostrar cliente não editável
        st.text_input("Cliente", value=cliente.get('empresa'), disabled=True)

        # Form para alterar
        with st.form("form_alterar_proc"):
            col1, col2 = st.columns([2, 1])
            with col1:
                codigo = st.text_input("Código / Identificação", value=proc.get('codigo', ''), max_chars=50)
                descricao = st.text_input("Nome do Processo", value=proc.get('descricao', ''), max_chars=255)
                
                # Ações
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar")
            with btn_col2:
                cancelar = st.form_submit_button("Cancelar")

            if cancelar:
                st.session_state.proc_selecionada = None
                st.session_state.proc_aba = "Listar"
                st.rerun()

            if salvar:
                cliente_id = (
                    cliente.get("id")
                    or cliente.get("id_cliente")
                )

                try:
                    proc_id = proc.get('id')
                    alterar_proc(proc_id, codigo, descricao)
                    st.success("Processo alterado com sucesso!")
                    st.session_state.proc_selecionada = None
                    st.session_state.proc_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao alterar processo: {e}")

elif st.session_state.proc_aba == "Excluir":
    st.subheader("Excluir Processo")

    if st.session_state.proc_selecionada is None:
        st.warning("Selecione um processo na lista antes de excluir.")
        if st.button("Voltar para lista"):
            st.session_state.proc_aba = "Listar"
            st.rerun()
    else:
        proc = st.session_state.proc_selecionada
        st.markdown(f"**Processo selecionado:** {proc.get('descricao')} ({proc.get('codigo')})")
        col_confirm, col_cancel = st.columns([1, 1])
        if col_cancel.button("Cancelar"):
            st.session_state.proc_selecionada = None
            st.session_state.proc_aba = "Listar"
            st.rerun()

        if col_confirm.button("Confirmar Exclusão ?"):
            try:
                proc_id = proc.get("id")
                excluir_proc(proc_id)
                st.success("Processo excluído com sucesso")
                st.session_state.proc_selecionada = None
                st.session_state.proc_aba = "Listar"
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao excluir processo: {e}")

