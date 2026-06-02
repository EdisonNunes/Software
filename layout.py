import streamlit as st
from pathlib import Path
import re

ROOT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = ROOT_DIR / ".streamlit" / "config.toml"

DEFAULT_THEME = "Black"
THEME_OPTIONS = ["Black", "White", "Custom"]
THEME_MAPPING = {
    "Black": "dark",
    "White": "light",
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


def read_theme_selection():
    theme = read_theme_config()
    if theme["backgroundColor"] or theme["secondaryBackgroundColor"]:
        return "Custom"
    if theme["base"] == "light":
        return "White"
    return "Black"


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


st.title("Layout")

current_theme = read_theme_selection()
config = read_theme_config()

selected_theme = st.radio("Escolha o tema de layout", THEME_OPTIONS, index=THEME_OPTIONS.index(current_theme))

custom_menu_color = config["secondaryBackgroundColor"] or "#111111"
custom_data_color = config["backgroundColor"] or "#0E1117"

if selected_theme == "Custom":
    st.markdown("### Tema pessoal")
    st.write("Escolha as cores da área de menu e da área de dados.")
    col1, col2 = st.columns(2)
    with col1:
        menu_color = st.color_picker("Cor da área de menu", value=custom_menu_color)
    with col2:
        data_color = st.color_picker("Cor da área de dados", value=custom_data_color)

    preview_html = f"""
    <div style='display:flex; gap:16px; margin-top:16px;'>
      <div style='flex:1; padding:16px; border-radius:12px; background:{menu_color}; color:{choose_text_color(menu_color)};'>
        <div style='font-size:14px; font-weight:700; margin-bottom:8px;'>Menu</div>
        <div style='font-size:12px;'>Cor escolhida: {menu_color}</div>
      </div>
      <div style='flex:1; padding:16px; border-radius:12px; background:{data_color}; color:{choose_text_color(data_color)};'>
        <div style='font-size:14px; font-weight:700; margin-bottom:8px;'>Área de dados</div>
        <div style='font-size:12px;'>Cor escolhida: {data_color}</div>
      </div>
    </div>
    """
    st.markdown(preview_html, unsafe_allow_html=True)

    preview_md = f"""
    ### Preview de tema customizado
    <div style='display:flex; gap:16px; margin-top:16px;'>
      <div style='flex:1; background:{menu_color}; border-radius:14px; padding:18px;'>
        <div style='color:{choose_text_color(menu_color)}; font-size:18px; font-weight:700; margin-bottom:8px;'>Menu</div>
        <div style='color:{choose_text_color(menu_color)}; font-size:14px;'>Navegação</div>
        <div style='color:{choose_text_color(menu_color)}; margin-top:12px;'>
          <div style="margin-bottom:6px;">• Item 1</div>
          <div style="margin-bottom:6px;">• Item 2</div>
          <div>• Item 3</div>
        </div>
      </div>
      <div style='flex:2; background:{data_color}; border-radius:14px; padding:18px;'>
        <div style='color:{choose_text_color(data_color)}; font-size:20px; font-weight:700; margin-bottom:12px;'>Área de dados</div>
        <div style='color:{choose_text_color(data_color)}; font-size:14px; margin-bottom:14px;'>Texto de exemplo, cabeçalho e botões no preview.</div>
        <div style='display:flex; gap:10px; flex-wrap:wrap;'>
          <span style='background:{menu_color}; color:{choose_text_color(menu_color)}; padding:10px 14px; border-radius:10px; font-weight:600;'>Botão 1</span>
          <span style='background:{menu_color}; color:{choose_text_color(menu_color)}; padding:10px 14px; border-radius:10px; font-weight:600;'>Botão 2</span>
        </div>
      </div>
    </div>
    """
    st.markdown(preview_md, unsafe_allow_html=True)
else:
    if selected_theme == "Black":
        menu_color = "#111111"
        data_color = "#0E1117"
        text_color = "#FFFFFF"
    else:
        menu_color = "#F1F3F5"
        data_color = "#FFFFFF"
        text_color = "#111111"

    default_preview = f"""
    ### Preview de tema {selected_theme}
    <div style='display:flex; gap:16px; margin-top:16px;'>
      <div style='flex:1; background:{menu_color}; border-radius:14px; padding:18px;'>
        <div style='color:{choose_text_color(menu_color)}; font-size:18px; font-weight:700; margin-bottom:8px;'>Menu</div>
        <div style='color:{choose_text_color(menu_color)}; font-size:14px;'>Navegação</div>
        <div style='color:{choose_text_color(menu_color)}; margin-top:12px;'>
          <div style="margin-bottom:6px;">• Item 1</div>
          <div style="margin-bottom:6px;">• Item 2</div>
          <div>• Item 3</div>
        </div>
      </div>
      <div style='flex:2; background:{data_color}; border-radius:14px; padding:18px;'>
        <div style='color:{choose_text_color(data_color)}; font-size:20px; font-weight:700; margin-bottom:12px;'>Área de dados</div>
        <div style='color:{choose_text_color(data_color)}; font-size:14px; margin-bottom:14px;'>Texto de exemplo, cabeçalho e botões no preview.</div>
        <div style='display:flex; gap:10px; flex-wrap:wrap;'>
          <span style='background:{menu_color}; color:{choose_text_color(menu_color)}; padding:10px 14px; border-radius:10px; font-weight:600;'>Botão 1</span>
          <span style='background:{menu_color}; color:{choose_text_color(menu_color)}; padding:10px 14px; border-radius:10px; font-weight:600;'>Botão 2</span>
        </div>
      </div>
    </div>
    """
    st.markdown(default_preview, unsafe_allow_html=True)

if st.button("Salvar"):
    if selected_theme == "Custom":
        menu_color = normalize_color(menu_color, custom_menu_color)
        data_color = normalize_color(data_color, custom_data_color)
        text_color = choose_text_color(data_color)
        write_theme_section({
            "base": "dark",
            "backgroundColor": data_color,
            "secondaryBackgroundColor": menu_color,
            "primaryColor": menu_color,
            "textColor": text_color,
        })
        st.success("Tema pessoal salvo. Atualize a página para aplicar as mudanças.")
    else:
        base = THEME_MAPPING[selected_theme]
        write_theme_section({
            "base": base,
            "backgroundColor": None,
            "secondaryBackgroundColor": None,
            "primaryColor": None,
            "textColor": None,
        })
        st.success(f"Layout alterado para {selected_theme}. Atualize a página para aplicar as mudanças.")

# st.write("\nConfiguração atual em `.streamlit/config.toml`:")
st.write("\nConfiguração atual :")
st.code(CONFIG_FILE.read_text(encoding="utf-8") if CONFIG_FILE.exists() else "(arquivo não existe)")
