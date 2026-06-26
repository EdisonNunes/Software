import streamlit as st

from pages.theme import read_streamlit_theme


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


def render_page_title_banner(title: str, icon_html: str = "&#128736;&#65039;") -> None:
	paleta = _banner_palette()
	st.markdown(
		f"""
		<div style="
			border: 1px solid {paleta['banner_border']};
			background: linear-gradient(135deg, {paleta['banner_bg']}, {paleta['banner_bg_soft']});
			border-radius: 18px;
			padding: 16px 20px;
			margin: 0.25rem 0 1rem 0;
			box-shadow: 0 10px 24px rgba(15, 23, 42, 0.18);
		">
			<div style="display:flex; align-items:center; gap:10px;">
				<span style="font-size:1.2rem; line-height:1;">{icon_html}</span>
				<div style="font-size: 1.35rem; font-weight: 800; color: {paleta['title_color']};">
					{title}
				</div>
			</div>
		</div>
		""",
		unsafe_allow_html=True,
	)


def render_cliente_banner(cliente: dict, total: int, total_label: str = "Registros") -> None:
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
				<span><strong>{total_label}:</strong> {total}</span>
			</div>
		</div>
		""",
		unsafe_allow_html=True,
	)