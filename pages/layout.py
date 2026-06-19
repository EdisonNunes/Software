import streamlit as st
from pathlib import Path
import re

from components.sidebar import render_app_sidebar
from components.top_menu import render_top_menu
from Pages.theme import apply_streamlit_theme


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT_DIR / ".streamlit" / "config.toml"

THEME_OPTIONS = [
    "Dark",
    "Light",
    "Personalizado 1 - Azul suave e profissional",
    "Personalizado 2 - Azul Mesclado",
    "Personalizado 3 - Tons de Cinza",
    "Personalizado 4 - Minimalista Escuro",
]

THEME_PRESETS = {
    "Personalizado 1 - Azul suave e profissional": {
        "base": "light",
        "backgroundColor": "#F4F7FA",
        "secondaryBackgroundColor": "#DCE6F1",
        "primaryColor": "#5A78D1",
        "textColor": "#1F2A44",
    },
    "Personalizado 2 - Azul Mesclado": {
        "base": "dark",
        "backgroundColor": "#1F1F3A",
        "secondaryBackgroundColor": "#0F172A",
        "primaryColor": "#6BBF59",
        "textColor": "#E8EDF8",
    },
    "Personalizado 3 - Tons de Cinza": {
        "base": "dark",
        "backgroundColor": "#34373F",
        "secondaryBackgroundColor": "#2B2F35",
        "primaryColor": "#7D7F85",
        "textColor": "#E3E5E8",
    },
    "Personalizado 4 - Minimalista Escuro": {
        "base": "dark",
        "backgroundColor": "#11131A",
        "secondaryBackgroundColor": "#1C2330",
        "primaryColor": "#8AA6C1",
        "textColor": "#E8EDF8",
    },
}


def read_theme_config():
    theme = {
        "base": None,
        "backgroundColor": None,
        "secondaryBackgroundColor": None,
        "primaryColor": None,
        "textColor": None,
    }

    if not CONFIG_FILE.exists():
        return theme

    content = CONFIG_FILE.read_text(encoding="utf-8")
    for key in theme.keys():
        match = re.search(rf"^{key}\s*=\s*['\"]([^'\"]+)['\"]", content, flags=re.MULTILINE)
        if match:
            theme[key] = match.group(1)

    return theme


def section_to_text(props: dict) -> str:
    lines = ["[theme]"]
    for key, value in props.items():
        if value is not None:
            lines.append(f"{key} = '{value}'")
    return "\n".join(lines) + "\n"


def write_theme_section(props: dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    content = CONFIG_FILE.read_text(encoding="utf-8") if CONFIG_FILE.exists() else ""
    new_section = section_to_text(props)

    if "[theme]" in content:
        content = re.sub(r"\[theme\].*?(?=\n\[|$)", new_section, content, flags=re.DOTALL)
    else:
        content = new_section + content

    CONFIG_FILE.write_text(content, encoding="utf-8")


def find_preset_for_theme(theme: dict) -> str:
    for preset_name, preset_values in THEME_PRESETS.items():
        if all(theme.get(key) == preset_values.get(key) for key in preset_values):
            return preset_name
    return ""


def read_theme_selection():
    theme = read_theme_config()
    preset = find_preset_for_theme(theme)
    if preset:
        return preset

    if theme["base"] == "light":
        return "Light"
    if theme["base"] == "dark":
        return "Dark"
    if theme["base"] == "custom":
        if theme["backgroundColor"]:
            hex_value = theme["backgroundColor"].lstrip("#")
            if len(hex_value) == 3:
                hex_value = "".join([c * 2 for c in hex_value])
            r, g, b = int(hex_value[0:2], 16), int(hex_value[2:4], 16), int(hex_value[4:6], 16)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            return "Light" if brightness > 128 else "Dark"
    return "Dark"


def normalize_color(value: str, default: str):
    if not value:
        return default
    return value if value.startswith("#") else f"#{value}"


def choose_text_color(background_hex: str) -> str:
    hex_value = background_hex.lstrip("#")
    if len(hex_value) == 3:
        hex_value = "".join([c * 2 for c in hex_value])
    r, g, b = int(hex_value[0:2], 16), int(hex_value[2:4], 16), int(hex_value[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#000000" if brightness > 128 else "#FFFFFF"


if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

apply_streamlit_theme()
render_app_sidebar()
render_top_menu()

st.info("# Layout", icon=":material/format_paint:")

current_theme = read_theme_selection()

selected_theme = st.radio(
    "Escolha o tema de layout",
    THEME_OPTIONS,
    index=THEME_OPTIONS.index(current_theme) if current_theme in THEME_OPTIONS else 0,
)

if selected_theme in THEME_PRESETS:
    theme_values = THEME_PRESETS[selected_theme]
    st.markdown(f"### {selected_theme}")
    st.write("Tema personalizado pré-configurado com cores e visualização de exemplo.")
else:
    theme_values = {
        "base": "dark" if selected_theme == "Dark" else "light",
        "backgroundColor": None,
        "secondaryBackgroundColor": None,
        "primaryColor": None,
        "textColor": None,
    }
    st.markdown(f"### Tema {selected_theme}")
    st.write("Tema padrão do Streamlit.")

background_color = theme_values["backgroundColor"] or ("#0E1117" if selected_theme == "Dark" else "#FFFFFF")
secondary_color = theme_values["secondaryBackgroundColor"] or ("#111111" if selected_theme == "Dark" else "#F1F3F5")
primary_color = theme_values["primaryColor"] or ("#111111" if selected_theme == "Dark" else "#F1F3F5")
text_color = theme_values["textColor"] or ("#FFFFFF" if selected_theme == "Dark" else "#111111")

# Mostra os valores do tema
col1, col2 = st.columns(2)
with col1:
    st.text_input("backgroundColor", value=background_color, disabled=True)
    st.text_input("primaryColor", value=primary_color, disabled=True)
with col2:
    st.text_input("secondaryBackgroundColor", value=secondary_color, disabled=True)
    st.text_input("textColor", value=text_color, disabled=True)

# Preview de cada cor individual
preview_colors = f"""
<div style='display:grid; grid-template-columns: repeat(2, 1fr); gap:12px; margin-top:16px;'>
  <div style='padding:12px; border-radius:10px; background:{background_color}; border:2px solid #333;'>
    <div style='color:{choose_text_color(background_color)}; font-size:12px; font-weight:700; margin-bottom:4px;'>backgroundColor</div>
    <div style='color:{choose_text_color(background_color)}; font-size:10px;'>{background_color}</div>
  </div>
  <div style='padding:12px; border-radius:10px; background:{secondary_color}; border:2px solid #333;'>
    <div style='color:{choose_text_color(secondary_color)}; font-size:12px; font-weight:700; margin-bottom:4px;'>secondaryBackgroundColor</div>
    <div style='color:{choose_text_color(secondary_color)}; font-size:10px;'>{secondary_color}</div>
  </div>
  <div style='padding:12px; border-radius:10px; background:{primary_color}; border:2px solid #333;'>
    <div style='color:{choose_text_color(primary_color)}; font-size:12px; font-weight:700; margin-bottom:4px;'>primaryColor</div>
    <div style='color:{choose_text_color(primary_color)}; font-size:10px;'>{primary_color}</div>
  </div>
  <div style='padding:12px; border-radius:10px; background:{background_color}; border:2px solid #666;'>
    <div style='color:{choose_text_color(background_color)}; font-size:12px; font-weight:700; margin-bottom:4px;'>textColor</div>
    <div style='color:{choose_text_color(background_color)}; font-size:10px;'>{text_color}</div>
  </div>
</div>
"""
st.markdown(preview_colors, unsafe_allow_html=True)

preview_md = f"""
### Preview completo do tema selecionado
<div style='display:flex; gap:16px; margin-top:16px;'>
  <div style='flex:1; background:{secondary_color}; border-radius:14px; padding:18px;'>
    <div style='color:{choose_text_color(secondary_color)}; font-size:18px; font-weight:700; margin-bottom:8px;'>Menu (Sidebar)</div>
    <div style='color:{choose_text_color(secondary_color)}; font-size:14px;'>Navegação</div>
    <div style='color:{choose_text_color(secondary_color)}; margin-top:12px;'>
      <div style="margin-bottom:8px; padding:8px; background:{background_color}; border-radius:6px; color:{choose_text_color(background_color)}; border-left:4px solid {primary_color};">• Item 1</div>
      <div style="margin-bottom:8px; padding:8px; background:{background_color}; border-radius:6px; color:{choose_text_color(background_color)}; border-left:4px solid {primary_color};">• Item 2</div>
      <div style="padding:8px; background:{background_color}; border-radius:6px; color:{choose_text_color(background_color)}; border-left:4px solid {primary_color};">• Item 3</div>
    </div>
  </div>
  <div style='flex:2; background:{background_color}; border-radius:14px; padding:18px;'>
    <div style='color:{choose_text_color(background_color)}; font-size:20px; font-weight:700; margin-bottom:12px;'>Área de dados</div>
    <div style='color:{choose_text_color(background_color)}; font-size:14px; margin-bottom:14px;'>Exemplo de conteúdo principal com as cores do tema selecionado.</div>
    <div style='display:flex; gap:10px; flex-wrap:wrap;'>
      <span style='background:{primary_color}; color:{choose_text_color(primary_color)}; padding:10px 14px; border-radius:10px; font-weight:600;'>Botão Primário</span>
      <span style='background:{secondary_color}; color:{choose_text_color(secondary_color)}; padding:10px 14px; border-radius:10px; font-weight:600; border:2px solid {primary_color};'>Botão Secundário</span>
    </div>
  </div>
</div>
"""
st.markdown(preview_md, unsafe_allow_html=True)

if st.button("Salvar", key="layout_salvar_tema"):
    if selected_theme in THEME_PRESETS:
        write_theme_section(theme_values)
        apply_streamlit_theme()
        st.success(f"Tema {selected_theme} salvo e aplicado.")
    else:
        write_theme_section({
            "base": theme_values["base"],
            "backgroundColor": None,
            "secondaryBackgroundColor": None,
            "primaryColor": None,
            "textColor": None,
        })
        apply_streamlit_theme()
        st.success(f"Tema {selected_theme} salvo e aplicado.")

st.write("\nConfiguração atual :")
st.code(CONFIG_FILE.read_text(encoding="utf-8") if CONFIG_FILE.exists() else "(arquivo não existe)")
