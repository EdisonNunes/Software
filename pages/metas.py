from decimal import Decimal, InvalidOperation
import re

import pandas as pd
import streamlit as st

from components.session_state import ensure_session_state
from components.sidebar import render_app_sidebar
from components.top_menu import render_top_menu
from components.page_banner import render_cliente_banner
from pages.theme import read_streamlit_theme
from pages import crud as crud_module
from pages.crud import listar_clientes, supabase


def _listar_metas_fallback(cliente_id=""):
	query = (
		supabase
		.table("metas")
		.select(
			"""
			id,
			parametro,
			descricao,
			valor,
			ativo,
			cliente_id
			"""
		)
	)

	if cliente_id:
		query = query.eq("cliente_id", cliente_id)

	response = query.order("parametro", desc=False).execute()
	return response.data


def _listar_todos_dados_metas_fallback(cliente_id=""):
	query = supabase.table("metas").select("*")

	if cliente_id:
		query = query.eq("cliente_id", cliente_id)

	response = query.order("parametro", desc=False).execute()
	return response.data


def _incluir_meta_fallback(parametro, descricao, valor, cliente_id, ativo=True):
	response = (
		supabase
		.table("metas")
		.insert(
			{
				"parametro": parametro,
				"descricao": descricao,
				"valor": valor,
				"cliente_id": cliente_id,
				"ativo": ativo,
			}
		)
		.execute()
	)
	return response.data


def _alterar_meta_fallback(meta_id, valor, ativo=None):
	update_payload = {"valor": valor}
	if ativo is not None:
		update_payload["ativo"] = ativo

	response = (
		supabase
		.table("metas")
		.update(update_payload)
		.eq("id", meta_id)
		.execute()
	)
	return response.data


listar_metas = getattr(crud_module, "listar_metas", _listar_metas_fallback)
listar_todos_dados_metas = getattr(
	crud_module,
	"listar_todos_dados_metas",
	_listar_todos_dados_metas_fallback,
)
incluir_meta = getattr(crud_module, "incluir_meta", _incluir_meta_fallback)
alterar_meta = getattr(crud_module, "alterar_meta", _alterar_meta_fallback)


def _normalizar_valor(valor: str) -> str:
	valor_limpo = (valor or "").strip().replace("%", "")

	if not valor_limpo:
		raise ValueError("Informe o valor da meta.")

	valor_normalizado = valor_limpo.replace(",", ".")

	try:
		valor_decimal = Decimal(valor_normalizado)
	except InvalidOperation as exc:
		raise ValueError("Valor deve ser numérico.") from exc

	if valor_decimal < 0:
		raise ValueError("Valor não pode ser negativo.")

	texto = format(valor_decimal.normalize(), "f")
	if "." in texto:
		texto = texto.rstrip("0").rstrip(".")

	return texto.replace(".", ",")


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


def _cards_palette() -> dict[str, str]:
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

	card_bg = _misturar(bg_rgb, sec_rgb, 0.72)
	card_bg_soft = _misturar(sec_rgb, bg_rgb, 0.78)
	card_border = _misturar(text_rgb, sec_rgb, 0.40)
	highlight_bg = _misturar(pri_rgb, card_bg, 0.18)
	highlight_border = _misturar(pri_rgb, card_border, 0.72)
	badge_bg = _misturar(pri_rgb, card_bg, 0.25)
	badge_text = _contraste_texto(badge_bg)
	title_color = _contraste_texto(card_bg)
	body_color = "rgb({},{},{})".format(*_misturar(text_rgb, bg_rgb, 0.82))
	label_color = "rgb({},{},{})".format(*_misturar(pri_rgb, text_rgb, 0.45))
	value_color = _contraste_texto(highlight_bg)

	return {
		"card_bg": f"rgb({card_bg[0]},{card_bg[1]},{card_bg[2]})",
		"card_bg_soft": f"rgb({card_bg_soft[0]},{card_bg_soft[1]},{card_bg_soft[2]})",
		"card_border": f"rgb({card_border[0]},{card_border[1]},{card_border[2]})",
		"highlight_bg": f"rgb({highlight_bg[0]},{highlight_bg[1]},{highlight_bg[2]})",
		"highlight_border": f"rgb({highlight_border[0]},{highlight_border[1]},{highlight_border[2]})",
		"badge_bg": f"rgba({badge_bg[0]},{badge_bg[1]},{badge_bg[2]},0.42)",
		"badge_text": badge_text,
		"title_color": title_color,
		"body_color": body_color,
		"label_color": label_color,
		"value_color": value_color,
	}


def _render_cliente_banner(cliente: dict, total_metas: int) -> None:
	render_cliente_banner(cliente, total_metas, total_label="Metas")


def _eh_escala_fmea(meta: dict) -> bool:
	return (meta.get("parametro") or "").strip().lower() == "escala fmea"


def _obter_intervalo_fmea(valor: str) -> tuple[int, int]:
	numeros = re.findall(r"\d+", valor or "")
	if len(numeros) >= 2:
		return int(numeros[0]), int(numeros[1])
	return 1, 5


def _formatar_valor_meta(meta: dict) -> str:
	valor = meta.get("valor", "-")
	if not _eh_escala_fmea(meta):
		return valor

	minimo, maximo = _obter_intervalo_fmea(valor)
	return f"Intervalo de {minimo} a {maximo}"


def _render_meta_cards(metas: list[dict], selected_id: str | None) -> dict | None:
	if not metas:
		st.info("Nenhuma meta cadastrada para este cliente.")
		return None

	paleta = _cards_palette()
	meta_escolhida = None

	for inicio in range(0, len(metas), 3):
		colunas = st.columns(3)
		for coluna, meta in zip(colunas, metas[inicio:inicio + 3]):
			destaque = meta.get("id") == selected_id
			borda = paleta["highlight_border"] if destaque else paleta["card_border"]
			fundo = (
				f"linear-gradient(160deg, {paleta['highlight_bg']}, {paleta['card_bg_soft']})"
				if destaque
				else f"linear-gradient(160deg, {paleta['card_bg']}, {paleta['card_bg_soft']})"
			)
			status = "Ativa" if meta.get("ativo", True) else "Inativa"

			with coluna:
				st.markdown(
					f"""
					<div style="
						min-height: 180px;
						border: 1px solid {borda};
						background: {fundo};
						border-radius: 18px;
						padding: 18px;
						margin-bottom: 1rem;
						box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
					">
						<div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
							<div style="font-size:1.05rem; font-weight:700; color:{paleta['title_color']};">
								{meta.get('parametro', '')}
							</div>
							<div style="font-size:0.78rem; color:{paleta['badge_text']}; background:{paleta['badge_bg']}; padding:4px 10px; border-radius:999px; font-weight:700;">
								{status}
							</div>
						</div>
						<div style="margin-top:0.85rem; color:{paleta['body_color']}; font-size:0.94rem; min-height:42px;">
							{meta.get('descricao', '') or 'Sem descrição cadastrada.'}
						</div>
						<div style="margin-top:1.1rem; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.08em; color:{paleta['label_color']};">
							Valor atual
						</div>
						<div style="font-size:1.8rem; font-weight:800; color:{paleta['value_color']}; margin-top:0.15rem;">
								{_formatar_valor_meta(meta)}
						</div>
					</div>
					""",
					unsafe_allow_html=True,
				)
				if st.button(
					"Alterar valor",
					key=f"meta_alterar_{meta.get('id')}",
					width='stretch',
				):
					meta_escolhida = meta

	return meta_escolhida


if not st.session_state.get("authenticated", False):
	st.switch_page("main.py")

render_app_sidebar()
render_top_menu()

st.info("# Cadastro de Metas", icon=":material/track_changes:")

ensure_session_state(
	{
		"metas_aba": "Listar",
		"metas_pagina": 0,
		"metas_busca_descricao": "",
		"metas_selecionada": None,
		"metas_cliente_selecionado": None,
		"metas_cliente_pagina": 0,
	}
)

if st.session_state.metas_aba == "Incluir":
	st.session_state.metas_aba = "Listar"

if st.session_state.get("role") not in ["admin", "supervisor"]:
	if st.session_state.metas_cliente_selecionado is None and st.session_state.get("cliente"):
		st.session_state.metas_cliente_selecionado = st.session_state.cliente

PAGE_SIZE = 10

if st.session_state.metas_aba == "Listar":
	if st.session_state.get("role") in ["admin", "supervisor"]:
		busca_atual = st.text_input("Buscar cliente", st.session_state.metas_busca_descricao)
		if busca_atual != st.session_state.metas_busca_descricao:
			st.session_state.metas_busca_descricao = busca_atual
			st.session_state.metas_cliente_pagina = 0
			st.rerun()

	if st.session_state.metas_cliente_selecionado is None:
		if st.session_state.get("role") in ["admin", "supervisor"]:
			clientes = listar_clientes(filtro_empresa=st.session_state.metas_busca_descricao)
			total = len(clientes)
			inicio = st.session_state.metas_cliente_pagina * PAGE_SIZE
			fim = inicio + PAGE_SIZE

			st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

			if clientes:
				clientes_paginados = clientes[inicio:fim]
				df_clientes = pd.DataFrame(clientes_paginados).copy()
				df_clientes["Selecionar"] = False

				selecao_cli = st.data_editor(
					df_clientes[["Selecionar", "empresa", "cidade", "telefone", "contato"]].reset_index(drop=True),
					hide_index=True,
					column_config={
						"Selecionar": st.column_config.CheckboxColumn("Selecionar", help="Marque para selecionar"),
						"empresa": st.column_config.TextColumn("Empresa"),
						"cidade": st.column_config.TextColumn("Cidade"),
						"telefone": st.column_config.TextColumn("Telefone"),
						"contato": st.column_config.TextColumn("Contato"),
					},
					key="metas_grid_clientes",
				)

				selecionados_cli = selecao_cli[selecao_cli["Selecionar"] == True]

				if len(selecionados_cli) == 1:
					idx = selecionados_cli.index[0]
					if idx < len(clientes_paginados):
						st.session_state.metas_cliente_selecionado = clientes_paginados[idx]
						st.session_state.metas_selecionada = None
						st.rerun()
				elif len(selecionados_cli) > 1:
					st.error("Selecione apenas 1 cliente por vez.")

			col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
			total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
			if col_pag1.button("⬅️", disabled=st.session_state.metas_cliente_pagina <= 0):
				st.session_state.metas_cliente_pagina -= 1
				st.rerun()
			col_pag2.write(f"Página {st.session_state.metas_cliente_pagina + 1} de {total_paginas}")
			if col_pag3.button("➡️", disabled=(st.session_state.metas_cliente_pagina + 1) >= total_paginas):
				st.session_state.metas_cliente_pagina += 1
				st.rerun()

			st.stop()
		else:
			if st.session_state.get("cliente"):
				st.session_state.metas_cliente_selecionado = st.session_state.cliente
				st.rerun()
			st.error("Empresa do usuário não encontrada.")
			st.stop()

	cliente = st.session_state.metas_cliente_selecionado
	cliente_id = cliente.get("id") or cliente.get("id_cliente") if cliente else None
	metas = listar_metas(cliente_id) if cliente_id else []

	_render_cliente_banner(cliente, len(metas))
	meta_escolhida = _render_meta_cards(metas, (st.session_state.metas_selecionada or {}).get("id"))

	if meta_escolhida is not None:
		st.session_state.metas_selecionada = meta_escolhida
		st.session_state.metas_aba = "Alterar"
		st.rerun()
	elif not metas:
		st.session_state.metas_selecionada = None

elif st.session_state.metas_aba == "Alterar":
	st.subheader("Alterar Meta")

	if st.session_state.metas_selecionada is None:
		st.warning("Selecione uma meta antes de alterar.")
		if st.button("Voltar para lista"):
			st.session_state.metas_aba = "Listar"
			st.rerun()
	else:
		meta = st.session_state.metas_selecionada
		cliente = st.session_state.metas_cliente_selecionado
		cliente_id = cliente.get("id") or cliente.get("id_cliente")
		_render_cliente_banner(cliente, len(listar_metas(cliente_id)))
		eh_escala_fmea = _eh_escala_fmea(meta)
		minimo_inicial, maximo_inicial = _obter_intervalo_fmea(meta.get("valor", ""))

		with st.form("form_alterar_meta"):
			with st.container(border=True):
				col_esq, col_dir = st.columns(2)

				with col_esq:
					st.text_input("Parâmetro", value=meta.get("parametro", ""), disabled=True)

					if eh_escala_fmea:
						col_min, col_max = st.columns(2)
						with col_min:
							valor_minimo = st.number_input(
								"Valor mínimo",
								min_value=0,
								value=int(minimo_inicial),
								step=1,
							)
						with col_max:
							valor_maximo = st.number_input(
								"Valor máximo",
								min_value=0,
								value=int(maximo_inicial),
								step=1,
							)
					else:
						valor = st.text_input("Valor", value=meta.get("valor", ""), max_chars=30)

				with col_dir:
					st.text_input("Descrição", value=meta.get("descricao", ""), disabled=True)
					ativo = st.checkbox("Meta ativa", value=bool(meta.get("ativo", True)))

			btn_col1, btn_col2 = st.columns([1, 1])
			with btn_col1:
				salvar = st.form_submit_button("Salvar", width='stretch')
			with btn_col2:
				cancelar = st.form_submit_button("Cancelar", width='stretch')

			if cancelar:
				st.session_state.metas_aba = "Listar"
				st.rerun()

			if salvar:
				try:
					if eh_escala_fmea:
						if valor_minimo > valor_maximo:
							raise ValueError("O valor mínimo não pode ser maior que o máximo.")
						valor_normalizado = f"{int(valor_minimo)}-{int(valor_maximo)}"
					else:
						valor_normalizado = _normalizar_valor(valor)

					alterar_meta(meta.get("id"), valor_normalizado, ativo)
					st.success("Meta alterada com sucesso!")
					st.session_state.metas_selecionada = None
					st.session_state.metas_aba = "Listar"
					st.rerun()
				except Exception as e:
					st.error(str(e))
