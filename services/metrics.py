import streamlit as st
import pandas as pd
from pathlib import Path
import re

def read_streamlit_theme():
    config_path = Path(__file__).resolve().parents[1] / ".streamlit" / "config.toml"
    if not config_path.exists():
        return {}
    content = config_path.read_text(encoding="utf-8")
    result = {}
    for key in ["base", "backgroundColor", "secondaryBackgroundColor", "textColor", "primaryColor"]:
        match = re.search(rf"^{key}\s*=\s*['\"]([^'\"]+)['\"]", content, flags=re.MULTILINE)
        if match:
            result[key] = match.group(1)

    theme_base = result.get("base")
    if theme_base == "dark":
        result.setdefault("backgroundColor", "#0F172A")
        result.setdefault("secondaryBackgroundColor", "#1E293B")
        result.setdefault("textColor", "#E2E8F0")
        result.setdefault("primaryColor", "#2563EB")
    elif theme_base == "light":
        result.setdefault("backgroundColor", "#FFFFFF")
        result.setdefault("secondaryBackgroundColor", "#F8FAFC")
        result.setdefault("textColor", "#0F172A")
        result.setdefault("primaryColor", "#2563EB")

    return result


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


def _mix(rgb_a: tuple[int, int, int], rgb_b: tuple[int, int, int], weight_a: float) -> tuple[int, int, int]:
    weight_a = max(0.0, min(1.0, weight_a))
    weight_b = 1.0 - weight_a
    return (
        int(rgb_a[0] * weight_a + rgb_b[0] * weight_b),
        int(rgb_a[1] * weight_a + rgb_b[1] * weight_b),
        int(rgb_a[2] * weight_a + rgb_b[2] * weight_b),
    )


def _contrast_text(rgb: tuple[int, int, int]) -> str:
    brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
    return "#0F172A" if brightness > 135 else "#F8FAFC"


def _theme_palette() -> dict[str, str]:
    theme = read_streamlit_theme()
    base = (theme.get("base") or "dark").lower()

    background_rgb = _hex_to_rgb(
        theme.get("backgroundColor", "#FFFFFF" if base == "light" else "#0F172A"),
        (255, 255, 255) if base == "light" else (15, 23, 42),
    )
    secondary_rgb = _hex_to_rgb(
        theme.get("secondaryBackgroundColor", "#F8FAFC" if base == "light" else "#1E293B"),
        (248, 250, 252) if base == "light" else (30, 41, 59),
    )
    primary_rgb = _hex_to_rgb(theme.get("primaryColor", "#2563EB"), (37, 99, 235))
    text_rgb = _hex_to_rgb(
        theme.get("textColor", "#0F172A" if base == "light" else "#E2E8F0"),
        (15, 23, 42) if base == "light" else (226, 232, 240),
    )

    card_bg = _mix(background_rgb, secondary_rgb, 0.70)
    card_bg_soft = _mix(secondary_rgb, background_rgb, 0.80)
    card_border = _mix(primary_rgb, secondary_rgb, 0.45)
    label_color = _mix(primary_rgb, text_rgb, 0.58)
    value_color = _contrast_text(card_bg)
    delta_bg = _mix(primary_rgb, card_bg, 0.25)
    delta_text = _contrast_text(delta_bg)
    page_bg = f"rgb({background_rgb[0]},{background_rgb[1]},{background_rgb[2]})"
    page_text = _contrast_text(background_rgb)

    return {
        "page_bg": page_bg,
        "page_text": page_text,
        "card_bg": f"rgb({card_bg[0]},{card_bg[1]},{card_bg[2]})",
        "card_bg_soft": f"rgb({card_bg_soft[0]},{card_bg_soft[1]},{card_bg_soft[2]})",
        "card_border": f"rgb({card_border[0]},{card_border[1]},{card_border[2]})",
        "label_color": f"rgb({label_color[0]},{label_color[1]},{label_color[2]})",
        "value_color": value_color,
        "delta_bg": f"rgba({delta_bg[0]},{delta_bg[1]},{delta_bg[2]},0.22)",
        "delta_text": delta_text,
    }

def metricas():
        data = pd.DataFrame({
                "Region": ["OEE Dia", "OEE Semnana", "OEE Mês"],
                "Sales": [0.83, 0.88, 0.86],
                "Growth": [-1.052, -0.03, .08]
        })
        meta_OEE = 0.85
        palette = _theme_palette()

        st.markdown(
                """
                <style>
                    .dashboard-wrap {
                        background: transparent;
                    }
                    .metric-card {
                        border: 1px solid %(card_border)s;
                        border-radius: 18px;
                        padding: 18px 16px;
                        background: linear-gradient(180deg, %(card_bg)s, %(card_bg_soft)s);
                        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.10);
                        min-height: 138px;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        text-align: center;
                    }
                    .metric-label {
                        font-size: 0.82rem;
                        text-transform: uppercase;
                        letter-spacing: 0.08em;
                        color: %(label_color)s;
                        font-weight: 700;
                        margin-bottom: 10px;
                    }
                    .metric-row {
                        display: flex;
                        align-items: baseline;
                        justify-content: center;
                        gap: 12px;
                        flex-wrap: wrap;
                    }
                    .metric-value {
                        font-size: 2.2rem;
                        font-weight: 800;
                        color: %(value_color)s;
                        line-height: 1;
                    }
                    .metric-delta {
                        font-size: 1rem;
                        font-weight: 700;
                        color: %(delta_text)s;
                        padding: 4px 10px;
                        border-radius: 999px;
                        background: %(delta_bg)s;
                    }
                    .dashboard-title {
                        color: %(page_text)s;
                        text-align: center;
                        margin-bottom: 0.75rem;
                    }
                </style>
                """ % palette,
                unsafe_allow_html=True,
        )

        st.markdown('<div class="dashboard-wrap">', unsafe_allow_html=True)
        cols = st.columns(len(data))

        for index, row in data.iterrows():
                diferenca_meta = row["Sales"] - meta_OEE
                cols[index].markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-label">{row['Region']} | meta: {meta_OEE:.0%}</div>
                            <div class="metric-row">
                                <div class="metric-value">{row['Sales']:.0%}</div>
                                <div class="metric-delta">{diferenca_meta:+.0%}  meta</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="dashboard-title"><h1>📊 Indicadores de Performance</h1></div>', unsafe_allow_html=True)
    metricas()