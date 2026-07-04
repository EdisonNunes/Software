import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd

from pages.theme import read_streamlit_theme
from pages.crud import supabase, listar_clientes, listar_todos_dados_clientes, listar_produtos, listar_todos_dados_produtos, incluir_produto, alterar_produto, excluir_produto
from pages.crud import listar_todos_dados_equipamentos, listar_todos_dados_familias_produtos, listar_unidades

from components.top_menu import render_top_menu
from components.sidebar import render_app_sidebar
from components.session_state import ensure_session_state
from components.page_banner import render_page_title_banner, render_cliente_banner


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
    render_cliente_banner(cliente, total_registros)


def _mensagem_erro_salvar_produto(erro: Exception, acao: str) -> str:
    mensagem = str(erro)
    if "duplicate key value violates unique constraint" in mensagem:
        return "Código já existente!"
    return f"Erro ao {acao} produto: {erro}"


if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

render_app_sidebar()

render_top_menu()

render_page_title_banner("Cadastro de Produtos [SKU]", icon_html="&#128230;")

ensure_session_state(
    {
        "sku_aba": "Listar",
        "sku_pagina": 0,
        "sku_busca_descricao": "",
        "sku_selecionado": None,
        "sku_cliente_selecionado": None,
        "sku_cliente_pagina": 0,
    }
)


PAGE_SIZE = 10

if st.session_state.sku_aba == "Listar":
    # Se nenhum cliente selecionado, primeiro mostrar grid de clientes
    if st.session_state.get("role") in ["admin", "supervisor"]:
        busca_atual = st.text_input("Buscar cliente", st.session_state.sku_busca_descricao)
        if busca_atual != st.session_state.sku_busca_descricao:
            st.session_state.sku_busca_descricao = busca_atual
            st.session_state.sku_cliente_pagina = 0
            st.session_state.sku_pagina = 0
            st.rerun()

    if st.session_state.sku_cliente_selecionado is None:
        # Admin e Supervisor escolhem a empresa
        if st.session_state.get("role") in ["admin", "supervisor"]:
            clientes = listar_clientes(filtro_empresa=st.session_state.sku_busca_descricao)

            total = len(clientes)
            inicio = st.session_state.sku_cliente_pagina * PAGE_SIZE
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
                    key="produtos_grid_clientes"
                )

                selecionados_cli = selecao_cli[selecao_cli["Selecionar"] == True]
                if len(selecionados_cli) == 1:
                    idx = selecionados_cli.index[0]
                    if idx < len(clientes_paginados):
                        id_selecionado = clientes_paginados[idx].get("id") or clientes_paginados[idx].get("id_cliente")
                        cliente_completo = next((c for c in listar_todos_dados_clientes() if (c.get("id") == id_selecionado or c.get("id_cliente") == id_selecionado)), None)
                        if cliente_completo:
                            st.session_state.sku_cliente_selecionado = cliente_completo
                            st.session_state.sku_pagina = 0
                            st.rerun()
                elif len(selecionados_cli) > 1:
                    st.error("Selecione apenas 1 cliente por vez.")

            # Paginação de clientes
            col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
            total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            if col_pag1.button("⬅️", disabled=st.session_state.sku_cliente_pagina <= 0):
                st.session_state.sku_cliente_pagina -= 1
                st.rerun()
            col_pag2.write(f"Página {st.session_state.sku_cliente_pagina + 1} de {total_paginas}")
            if col_pag3.button("➡️", disabled=(st.session_state.sku_cliente_pagina + 1) >= total_paginas):
                st.session_state.sku_cliente_pagina += 1
                st.rerun()

            # Não mostrar botões de ação antes da seleção do cliente
            st.stop()
         # Gerente e Funcionário usam automaticamente sua empresa
        else:
            cliente_completo = next((c for c in listar_todos_dados_clientes()
                    if c.get("id") == st.session_state.get("cliente_id")), None)
            if cliente_completo:
                st.session_state.sku_cliente_selecionado = (cliente_completo)
                st.rerun()

    # Se chegou aqui, há um cliente selecionado: mostrar produtos apenas deste cliente
    cliente = st.session_state.sku_cliente_selecionado

    if cliente:
        produtos = listar_produtos(filtro_produto=cliente.get('id') or cliente.get('id_cliente'))
    else:
        produtos = []

    if cliente and st.session_state.get("role") in ["admin", "supervisor"]:
        _render_cliente_banner(cliente, len(produtos))
        if st.button("Limpar seleção de cliente"):
            st.session_state.sku_cliente_selecionado = None
            st.rerun()

    total = len(produtos)
    inicio = st.session_state.sku_pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE
    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

    if produtos:
        produtos_paginados = produtos[inicio:fim]
        df_exibicao = pd.DataFrame(produtos_paginados).copy()
        df_exibicao["Selecionar"] = False
        # df_exibicao["id_produto"] = df_exibicao["id_produto"].astype(str)

        # Colunas e Configuração
        cols_exibicao = ["Selecionar", "codigo", "descricao", "equipamento", "familia", "lote_padrao", "tempo_ciclo"]
        
        selecao = st.data_editor(
            df_exibicao[cols_exibicao].reset_index(drop=True),
            hide_index=True,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Selecionar", help="Marque para selecionar"),
                "codigo": st.column_config.TextColumn("Código"),
                "descricao": st.column_config.TextColumn("Descrição"),
                "equipamento": st.column_config.TextColumn("Equipamento"),
                "familia": st.column_config.TextColumn("Família"),
                "lote_padrao": st.column_config.NumberColumn("Lote Padrão", format="%.2f"),
                "tempo_ciclo": st.column_config.NumberColumn("Tempo de Ciclo", format="%.2f"),
            },
            key="produtos_grid_produtos"
        )

        # Lógica de Seleção
        selecionados = selecao[selecao["Selecionar"] == True]

        if len(selecionados) == 1:
            idx_paginado = selecionados.index[0]
            if idx_paginado < len(produtos_paginados):
                id_selecionado = produtos_paginados[idx_paginado].get("id")

                produto_completo = next((c for c in listar_todos_dados_produtos() if c.get("id") == id_selecionado), None)

                if produto_completo:
                    st.session_state.sku_selecionado = produto_completo
        elif len(selecionados) > 1:
            st.error("Selecione apenas 1 produto por vez.")

    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    
    total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    if col_pag1.button("⬅️", disabled=st.session_state.sku_pagina <= 0):
        st.session_state.sku_pagina -= 1
        st.rerun()

    col_pag2.write(f"Página {st.session_state.sku_pagina + 1} de {total_paginas}")

    if col_pag3.button("➡️", disabled=(st.session_state.sku_pagina + 1) >= total_paginas):
        st.session_state.sku_pagina += 1
        st.rerun()

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Listar"):
            st.session_state.sku_aba = "Listar"
            st.rerun()
        if col2.button("Incluir"):
            st.session_state.sku_aba = "Incluir"
            st.rerun()
        if col3.button("Alterar", disabled=st.session_state.sku_selecionado is None):
            st.session_state.sku_aba = "Alterar"
            st.rerun()
        if col4.button("Excluir", disabled=st.session_state.sku_selecionado is None):
            st.session_state.sku_aba = "Excluir"
elif st.session_state.sku_aba == "Incluir":
    st.subheader("Incluir Produto")

    # Verifica se há cliente selecionado
    if st.session_state.sku_cliente_selecionado is None:
        st.warning("Selecione um cliente antes de incluir um produto.")
        if st.button("Escolher cliente"):
            st.session_state.sku_aba = "Listar"
            st.rerun()
    else:
        cliente = st.session_state.sku_cliente_selecionado
        # Exibir via componente HTML para garantir que estilo seja aplicado
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
        lista_familias = listar_todos_dados_familias_produtos(cliente.get('id') or cliente.get('id_cliente'))
        lista_equipamentos = []
        lista_equipamentos = listar_todos_dados_equipamentos(cliente.get('id') or cliente.get('id_cliente'))
        unidades_tempo = listar_unidades("Tempo")
        unidades_lote = listar_unidades(["Produção", "Quantidade", "Embalagem"])

        if not lista_familias:
            st.warning("Não há famílias de produto ativas para este cliente. Cadastre uma família para continuar.")
            if st.button("Voltar"):
                st.session_state.sku_aba = "Listar"
                st.rerun()
            st.stop()

        if not lista_equipamentos:
            st.warning("Não há equipamentos cadastrados para este cliente. Cadastre um equipamento para continuar.")
            if st.button("Voltar"):
                st.session_state.sku_aba = "Listar"
                st.rerun()
            st.stop()

        if not unidades_tempo or not unidades_lote:
            st.warning("Não há unidades suficientes cadastradas para tempo/lote.")
            if st.button("Voltar"):
                st.session_state.sku_aba = "Listar"
                st.rerun()
            st.stop()

        opcoes_familias = [item.get("id") for item in lista_familias]
        opcoes_equipamentos = [item.get("id") for item in lista_equipamentos]
        opcoes_unidade_tempo = [item.get("id") for item in unidades_tempo]
        opcoes_unidade_lote = [item.get("id") for item in unidades_lote]

        # Formulário aprimorado em colunas
        with st.form("form_incluir_produto"):
            col1, col2 = st.columns([1, 1])

            with col1:
                # Campo não editável com o cliente selecionado
                st.text_input("Cliente", value=cliente.get('empresa'), disabled=True)
                codigo = st.text_input("Código / Identificação", max_chars=50)
                descricao = st.text_input("Nome do Produto", max_chars=255)
                familia_id = st.selectbox(
                    "Família",
                    options=opcoes_familias,
                    format_func=lambda item_id: next((f.get("descricao", "") for f in lista_familias if f.get("id") == item_id), ""),
                )
                ean = st.text_input("EAN", max_chars=64)

            with col2:
                lote_padrao = st.number_input("Lote Padrão [Quantidade]", min_value=0.0, step=1.0, format="%f")
                unidade_lote_id = st.selectbox(
                    "Unidade do Lote",
                    options=opcoes_unidade_lote,
                    format_func=lambda item_id: next((f"{u.get('descricao')} ({u.get('codigo')})" for u in unidades_lote if u.get("id") == item_id), ""),
                )
                equipamento_id = st.selectbox(
                    "Equipamento",
                    options=opcoes_equipamentos,
                    format_func=lambda item_id: next((e.get("descricao", "") for e in lista_equipamentos if e.get("id") == item_id), ""),
                )
                equipamento_selecionado = next(
                    (
                        e for e in lista_equipamentos
                        if e.get("id") == equipamento_id
                    ),
                    {}
                )

                classificacao = equipamento_selecionado.get("classif","")
                st.text_input("Classificação",  value=classificacao, disabled=True)

                tempo_ciclo = st.number_input("Tempo de Ciclo", min_value=0.0, step=0.1)
                unidade_tempo_id = st.selectbox(
                    "Unidade de Tempo",
                    options=opcoes_unidade_tempo,
                    format_func=lambda item_id: next((f"{u.get('descricao')} ({u.get('codigo')})" for u in unidades_tempo if u.get("id") == item_id), ""),
                )

            # Botões lado-a-lado: Salvar e Sair sem Salvar
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar")
            with btn_col2:
                sair_sem_salvar = st.form_submit_button("Sair sem Salvar")

            if sair_sem_salvar:
                # Abandonar inclusão e voltar para seleção de cliente
                st.session_state.sku_cliente_selecionado = None
                st.session_state.sku_aba = "Listar"
                st.rerun()

            if salvar:
                novo_produto = {
                    "codigo": codigo,
                    "descricao": descricao,
                    "familia_id": familia_id,
                    "lote_padrao": lote_padrao,
                    "unidade_lote_id": unidade_lote_id,
                    "equipamento_id": equipamento_id,
                    "tempo_ciclo_padrao": tempo_ciclo,
                    "unidade_tempo_id": unidade_tempo_id,
                    "ean": ean,
                    "cliente_id": cliente.get("id") or cliente.get("id_cliente")
                }
                try:
                    incluir_produto(novo_produto)
                    st.success("Produto incluído com sucesso!")
                    # Limpar seleção de produto e voltar para listagem
                    st.session_state.sku_selecionado = None
                    st.session_state.sku_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(_mensagem_erro_salvar_produto(e, "incluir"))

elif st.session_state.sku_aba == "Alterar":
    st.subheader("Alterar Produto")

    if st.session_state.sku_selecionado is None:
        st.warning("Selecione um produto na lista antes de alterar.")
        if st.button("Voltar para lista"):
            st.session_state.sku_aba = "Listar"
            st.rerun()
    else:
        produto = st.session_state.sku_selecionado
        cliente = st.session_state.sku_cliente_selecionado

        # Mostrar cliente não editável
        st.text_input("Cliente", value=cliente.get('empresa'), disabled=True)
        lista_familias = listar_todos_dados_familias_produtos(cliente.get('id') or cliente.get('id_cliente'))
        lista_equipamentos = []
        lista_equipamentos = listar_todos_dados_equipamentos(cliente.get('id') or cliente.get('id_cliente'))
        unidades_tempo = listar_unidades("Tempo")
        unidades_lote = listar_unidades(["Produção", "Quantidade", "Embalagem"])

        opcoes_familias = [item.get("id") for item in lista_familias]
        opcoes_equipamentos = [item.get("id") for item in lista_equipamentos]
        opcoes_unidade_tempo = [item.get("id") for item in unidades_tempo]
        opcoes_unidade_lote = [item.get("id") for item in unidades_lote]

        familia_atual = produto.get("familia_id")
        equipamento_atual = produto.get("equipamento_id")
        unidade_tempo_atual = produto.get("unidade_tempo_id")
        unidade_lote_atual = produto.get("unidade_lote_id")

        # Fallback: se o valor atual existe no produto mas nao veio nos cadastros auxiliares,
        # inclui como opcao para permitir a alteracao sem bloquear o fluxo.
        if familia_atual and familia_atual not in opcoes_familias:
            opcoes_familias.append(familia_atual)
            lista_familias.append({"id": familia_atual, "descricao": "Atual (fora do cadastro ativo)"})

        if equipamento_atual and equipamento_atual not in opcoes_equipamentos:
            opcoes_equipamentos.append(equipamento_atual)
            lista_equipamentos.append({"id": equipamento_atual, "descricao": "Atual (fora do cadastro ativo)", "classif": ""})

        if unidade_tempo_atual and unidade_tempo_atual not in opcoes_unidade_tempo:
            opcoes_unidade_tempo.append(unidade_tempo_atual)
            unidades_tempo.append({"id": unidade_tempo_atual, "descricao": "Atual (fora do cadastro ativo)", "codigo": ""})

        if unidade_lote_atual and unidade_lote_atual not in opcoes_unidade_lote:
            opcoes_unidade_lote.append(unidade_lote_atual)
            unidades_lote.append({"id": unidade_lote_atual, "descricao": "Atual (fora do cadastro ativo)", "codigo": ""})

        if not opcoes_familias or not opcoes_equipamentos or not opcoes_unidade_tempo or not opcoes_unidade_lote:
            st.warning(
                "Cadastros auxiliares incompletos (famílias, equipamentos ou unidades) e não foi possível identificar os valores atuais do produto."
            )
            if st.button("Voltar para lista"):
                st.session_state.sku_aba = "Listar"
                st.rerun()
            st.stop()

        if familia_atual not in opcoes_familias:
            familia_atual = opcoes_familias[0]

        if equipamento_atual not in opcoes_equipamentos:
            equipamento_atual = opcoes_equipamentos[0]

        if unidade_tempo_atual not in opcoes_unidade_tempo:
            unidade_tempo_atual = opcoes_unidade_tempo[0]

        if unidade_lote_atual not in opcoes_unidade_lote:
            unidade_lote_atual = opcoes_unidade_lote[0]

        indice_equipamento = (
            opcoes_equipamentos.index(equipamento_atual)
            if equipamento_atual in opcoes_equipamentos
            else 0
        )

        # Form para alterar
        with st.form("form_alterar_produto"):
            col1, col2 = st.columns([1, 1])
            with col1:
                codigo = st.text_input("Código / Identificação", value=produto.get('codigo', ''), max_chars=50)
                descricao = st.text_input("Nome do Produto", value=produto.get('descricao', ''), max_chars=255)
                familia_id = st.selectbox(
                    "Família",
                    options=opcoes_familias,
                    index=opcoes_familias.index(familia_atual),
                    format_func=lambda item_id: next((f.get("descricao", "") for f in lista_familias if f.get("id") == item_id), ""),
                )
                ean = st.text_input("EAN", value=produto.get("ean", ""), max_chars=64)
            with col2:
                lote_padrao = st.number_input("Lote Padrão [Quantidade]", value=float(produto.get('lote_padrao') or 0.0), min_value=0.0, step=1.0, format="%f")
                unidade_lote_id = st.selectbox(
                    "Unidade do Lote",
                    options=opcoes_unidade_lote,
                    index=opcoes_unidade_lote.index(unidade_lote_atual),
                    format_func=lambda item_id: next((f"{u.get('descricao')} ({u.get('codigo')})" for u in unidades_lote if u.get("id") == item_id), ""),
                )
                equipamento_id = st.selectbox("Equipamento", options=opcoes_equipamentos, index=indice_equipamento, format_func=lambda item_id: next((e.get("descricao", "") for e in lista_equipamentos if e.get("id") == item_id), ""))
                #classificacao = st.text_input("Classificação", value=produto.get('classificacao', ''))
                equipamento_selecionado = next(
                                (
                                    e for e in lista_equipamentos
                                    if e.get("id") == equipamento_id
                                ),
                                {}  )

                classificacao = equipamento_selecionado.get("classif","")

                st.text_input("Classificação", value=classificacao, disabled=True)
                tempo_ciclo = st.number_input("Tempo de Ciclo", value=float(produto.get('tempo_ciclo') or 0.0), min_value=0.0, step=0.1)
                unidade_tempo_id = st.selectbox(
                    "Unidade de Tempo",
                    options=opcoes_unidade_tempo,
                    index=opcoes_unidade_tempo.index(unidade_tempo_atual),
                    format_func=lambda item_id: next((f"{u.get('descricao')} ({u.get('codigo')})" for u in unidades_tempo if u.get("id") == item_id), ""),
                )

            # Ações
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                salvar = st.form_submit_button("Salvar")
            with btn_col2:
                cancelar = st.form_submit_button("Cancelar")

            if cancelar:
                st.session_state.sku_selecionado = None
                st.session_state.sku_aba = "Listar"
                st.rerun()

            if salvar:
                dados = {
                    "codigo": codigo,
                    "descricao": descricao,
                    "familia_id": familia_id,
                    "lote_padrao": lote_padrao,
                    "unidade_lote_id": unidade_lote_id,
                    "equipamento_id": equipamento_id,
                    "tempo_ciclo_padrao": tempo_ciclo,
                    "unidade_tempo_id": unidade_tempo_id,
                    "ean": ean,
                    "cliente_id": cliente.get("id") or cliente.get("id_cliente")
                }
                try:
                    prod_id = produto.get('id')
                    alterar_produto(prod_id, dados)
                    st.success("Produto alterado com sucesso!")
                    st.session_state.sku_selecionado = None
                    st.session_state.sku_aba = "Listar"
                    st.rerun()
                except Exception as e:
                    st.error(_mensagem_erro_salvar_produto(e, "alterar"))

elif st.session_state.sku_aba == "Excluir":
    st.subheader("Excluir Produto")

    if st.session_state.sku_selecionado is None:
        st.warning("Selecione um produto na lista antes de excluir.")
        if st.button("Voltar para lista"):
            st.session_state.sku_aba = "Listar"
            st.rerun()
    else:
        produto = st.session_state.sku_selecionado
        st.markdown(f"**Produto selecionado:** {produto.get('descricao')} ({produto.get('codigo')})")
        col_confirm, col_cancel = st.columns([1, 1])
        if col_cancel.button("Cancelar"):
            st.session_state.sku_selecionado = None
            st.session_state.sku_aba = "Listar"
            st.rerun()
        if col_confirm.button("Confirmar Exclusão"):
            try:
                prod_id = produto.get('id')
                excluir_produto(prod_id)
                st.success("Produto excluído com sucesso")
                st.session_state.sku_selecionado = None
                st.session_state.sku_aba = "Listar"
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao excluir produto: {e}")

