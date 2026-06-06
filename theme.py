import re
from pathlib import Path

import streamlit as st


def read_streamlit_theme():
    config_path = Path(__file__).resolve().parent / ".streamlit" / "config.toml"
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


def apply_streamlit_theme():
    theme_colors = read_streamlit_theme()
    if not theme_colors:
        return

    background = theme_colors.get("backgroundColor")
    secondary = theme_colors.get("secondaryBackgroundColor")
    text = theme_colors.get("textColor")

    css = """
    <style>
      html, body, [data-testid='stAppViewContainer'], [data-testid='stAppViewContainer'] > div {
        background-color: %(background)s !important;
        color: %(text)s !important;
      }
      [data-testid='stSidebar'] {
        background-color: %(secondary)s !important;
        color: %(text)s !important;
      }
      [data-testid='stSidebar'] *,
      [data-testid='stSidebar'] span,
      [data-testid='stSidebar'] div,
      [data-testid='stSidebar'] label,
      [data-testid='stSidebar'] a,
      [data-testid='stSidebar'] p,
      [data-testid='stSidebar'] li {
        color: %(text)s !important;
      }
      [data-testid='stHeader'], [data-testid='stToolbar'], .css-1y0tads, .css-1d391kg, .css-18e3th9 {
        background-color: %(secondary)s !important;
        color: %(text)s !important;
      }
      [data-testid='stAppViewContainer'] input,
      [data-testid='stAppViewContainer'] textarea,
      [data-testid='stAppViewContainer'] select,
      [data-testid='stAppViewContainer'] button,
      [data-testid='stAppViewContainer'] .css-1x6t7y0, /* form fields */
      [data-testid='stAppViewContainer'] .css-1szy77t, /* text inputs */
      [data-testid='stAppViewContainer'] .css-1g3w1t5 {
        background-color: %(background)s !important;
        color: %(text)s !important;
      }
      [data-testid='stAppViewContainer'] button,
      [data-testid='stAppViewContainer'] .stButton button,
      [data-testid='stAppViewContainer'] input[type='submit'] {
        background-color: %(secondary)s !important;
        color: %(text)s !important;
        border-color: %(text)s !important;
      }
      [data-testid='stAppViewContainer'] [data-testid='stDataFrame'] table,
      [data-testid='stAppViewContainer'] [data-testid='stDataFrame'] th,
      [data-testid='stAppViewContainer'] [data-testid='stDataFrame'] td,
      [data-testid='stAppViewContainer'] [data-testid='stTable'] th,
      [data-testid='stAppViewContainer'] [data-testid='stTable'] td,
      [data-testid='stAppViewContainer'] [data-testid='stDataEditor'] th,
      [data-testid='stAppViewContainer'] [data-testid='stDataEditor'] td {
        background-color: %(background)s !important;
        color: %(text)s !important;
        border-color: %(text)s !important;
      }
      .css-1d391kg *, .css-1y0tads *, .css-18e3th9 * {
        color: %(text)s !important;
      }
      .css-1d391kg [data-testid='stMarkdownContainer'] {
        background-color: %(background)s !important;
      }
    </style>
    """ % {
        "background": background or "transparent",
        "secondary": secondary or background or "transparent",
        "text": text or "inherit",
    }

    st.markdown(css, unsafe_allow_html=True)

    hide_streamlit_style = """
        <style>
        html, body, [data-testid=\"stAppViewContainer\"], [data-testid=\"stAppViewContainer\"] * {
            font-size: 18px !important;
            line-height: 1.5 !important;
        }
        [data-testid=\"stAppViewContainer\"] h1,
        [data-testid=\"stAppViewContainer\"] h2,
        [data-testid=\"stAppViewContainer\"] h3,
        [data-testid=\"stAppViewContainer\"] h4,
        [data-testid=\"stAppViewContainer\"] h5,
        [data-testid=\"stAppViewContainer\"] h6 {
            font-size: 1.4em !important;
        }
        button[title=\"Open GitHub\"] {display: none;}
        button[title=\"Edit this app\"] {display: none;}
        /* Esconda ícones de configurações se necessário */
        [data-testid=\"stToolbar\"] {display: none;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
