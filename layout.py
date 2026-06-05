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

custom_background_color = config["backgroundColor"] or "#0E1117"
custom_secondary_color = config["secondaryBackgroundColor"] or "#111111"
custom_primary_color = config["primaryColor"] or "#111111"
custom_text_color = config["textColor"] or "#FFFFFF"

if selected_theme == "Custom":
    st.markdown("### Tema pessoal")
    st.write("Customize todas as cores do seu tema:")
    
    col1, col2 = st.columns(2)
    with col1:
        background_color = st.color_picker("Cor Área Dados (backgroundColor)", value=custom_background_color)
        primary_color = st.color_picker("Cor primária (primaryColor)", value=custom_primary_color)
    with col2:
        secondary_color = st.color_picker("Cor do Menu (BackgroundColor)", value=custom_secondary_color)
        text_color = st.color_picker("Cor do texto (textColor)", value=custom_text_color)

    # Preview das cores individuais
    preview_colors = f"""
    <div style='display:grid; grid-template-columns: repeat(2, 1fr); gap:12px; margin-top:16px;'>
      <div style='padding:12px; border-radius:10px; background:{background_color}; border:2px solid #333;'>
        <div style='color:{text_color}; font-size:12px; font-weight:700; margin-bottom:4px;'>backgroundColor</div>
        <div style='color:{text_color}; font-size:10px;'>{background_color}</div>
      </div>
      <div style='padding:12px; border-radius:10px; background:{secondary_color}; border:2px solid #333;'>
        <div style='color:{text_color}; font-size:12px; font-weight:700; margin-bottom:4px;'>secondaryBackgroundColor</div>
        <div style='color:{text_color}; font-size:10px;'>{secondary_color}</div>
      </div>
      <div style='padding:12px; border-radius:10px; background:{primary_color}; border:2px solid #333;'>
        <div style='color:{text_color}; font-size:12px; font-weight:700; margin-bottom:4px;'>primaryColor</div>
        <div style='color:{text_color}; font-size:10px;'>{primary_color}</div>
      </div>
      <div style='padding:12px; border-radius:10px; background:{background_color}; border:2px solid #666;'>
        <div style='color:{text_color}; font-size:12px; font-weight:700; margin-bottom:4px;'>textColor</div>
        <div style='color:{text_color}; font-size:10px;'>{text_color}</div>
      </div>
    </div>
    """
    st.markdown(preview_colors, unsafe_allow_html=True)

    # Preview completo do aplicativo com as cores escolhidas
    preview_md = f"""
    ### Preview completo do tema customizado
    <div style='display:flex; gap:16px; margin-top:16px;'>
      <div style='flex:1; background:{secondary_color}; border-radius:14px; padding:18px;'>
        <div style='color:{text_color}; font-size:18px; font-weight:700; margin-bottom:8px;'>Menu (Sidebar)</div>
        <div style='color:{text_color}; font-size:14px;'>Navegação</div>
        <div style='color:{text_color}; margin-top:12px;'>
          <div style="margin-bottom:8px; padding:8px; background:{background_color}; border-radius:6px; color:{text_color};border-left:4px solid {primary_color};">• Item 1</div>
          <div style="margin-bottom:8px; padding:8px; background:{background_color}; border-radius:6px; color:{text_color};border-left:4px solid {primary_color};">• Item 2</div>
          <div style="padding:8px; background:{background_color}; border-radius:6px; color:{text_color};border-left:4px solid {primary_color};">• Item 3</div>
        </div>
      </div>
      <div style='flex:2; background:{background_color}; border-radius:14px; padding:18px;'>
        <div style='color:{text_color}; font-size:20px; font-weight:700; margin-bottom:12px;'>Área de dados</div>
        <div style='color:{text_color}; font-size:14px; margin-bottom:14px;'>Exemplo de conteúdo principal com as cores selecionadas.</div>
        <div style='display:flex; gap:10px; flex-wrap:wrap;'>
          <span style='background:{primary_color}; color:{text_color}; padding:10px 14px; border-radius:10px; font-weight:600;'>Botão Primário</span>
          <span style='background:{secondary_color}; color:{text_color}; padding:10px 14px; border-radius:10px; font-weight:600; border:2px solid {primary_color};'>Botão Secundário</span>
        </div>
      </div>
    </div>
    """
    st.markdown(preview_md, unsafe_allow_html=True)
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
else:
    if selected_theme == "Black":
        menu_color = "#111111"
        data_color = "#0E1117"
        primary_color = "#111111"
        text_color = "#FFFFFF"
    else:
        menu_color = "#F1F3F5"
        data_color = "#FFFFFF"
        primary_color = "#F1F3F5"
        text_color = "#111111"

    # Exibir parâmetros em modo read-only
    st.markdown(f"### Parâmetros do tema {selected_theme}")
    st.info("Os parâmetros abaixo não podem ser alterados neste tema predefinido. Use Custom para editar todas as cores.")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("backgroundColor", value=data_color, disabled=True)
        st.text_input("primaryColor", value=primary_color, disabled=True)
    with col2:
        st.text_input("secondaryBackgroundColor", value=menu_color, disabled=True)
        st.text_input("textColor", value=text_color, disabled=True)

    # Preview das cores individuais
    preview_colors = f"""
    <div style='display:grid; grid-template-columns: repeat(2, 1fr); gap:12px; margin-top:16px;'>
      <div style='padding:12px; border-radius:10px; background:{data_color}; border:2px solid #333;'>
        <div style='color:{text_color}; font-size:12px; font-weight:700; margin-bottom:4px;'>backgroundColor</div>
        <div style='color:{text_color}; font-size:10px;'>{data_color}</div>
      </div>
      <div style='padding:12px; border-radius:10px; background:{menu_color}; border:2px solid #333;'>
        <div style='color:{text_color}; font-size:12px; font-weight:700; margin-bottom:4px;'>secondaryBackgroundColor</div>
        <div style='color:{text_color}; font-size:10px;'>{menu_color}</div>
      </div>
      <div style='padding:12px; border-radius:10px; background:{primary_color}; border:2px solid #333;'>
        <div style='color:{text_color}; font-size:12px; font-weight:700; margin-bottom:4px;'>primaryColor</div>
        <div style='color:{text_color}; font-size:10px;'>{primary_color}</div>
      </div>
      <div style='padding:12px; border-radius:10px; background:{data_color}; border:2px solid #666;'>
        <div style='color:{text_color}; font-size:12px; font-weight:700; margin-bottom:4px;'>textColor</div>
        <div style='color:{text_color}; font-size:10px;'>{text_color}</div>
      </div>
    </div>
    """
    st.markdown(preview_colors, unsafe_allow_html=True)

    # Preview completo do aplicativo
    default_preview = f"""
    ### Preview completo do tema {selected_theme}
    <div style='display:flex; gap:16px; margin-top:16px;'>
      <div style='flex:1; background:{menu_color}; border-radius:14px; padding:18px;'>
        <div style='color:{choose_text_color(menu_color)}; font-size:18px; font-weight:700; margin-bottom:8px;'>Menu (Sidebar)</div>
        <div style='color:{choose_text_color(menu_color)}; font-size:14px;'>Navegação</div>
        <div style='color:{choose_text_color(menu_color)}; margin-top:12px;'>
          <div style="margin-bottom:8px; padding:8px; background:{data_color}; border-radius:6px; color:{text_color};border-left:4px solid {primary_color};">• Item 1</div>
          <div style="margin-bottom:8px; padding:8px; background:{data_color}; border-radius:6px; color:{text_color};border-left:4px solid {primary_color};">• Item 2</div>
          <div style="padding:8px; background:{data_color}; border-radius:6px; color:{text_color};border-left:4px solid {primary_color};">• Item 3</div>
        </div>
      </div>
      <div style='flex:2; background:{data_color}; border-radius:14px; padding:18px;'>
        <div style='color:{choose_text_color(data_color)}; font-size:20px; font-weight:700; margin-bottom:12px;'>Área de dados</div>
        <div style='color:{choose_text_color(data_color)}; font-size:14px; margin-bottom:14px;'>Exemplo de conteúdo principal com as cores do tema {selected_theme}.</div>
        <div style='display:flex; gap:10px; flex-wrap:wrap;'>
          <span style='background:{primary_color}; color:{choose_text_color(primary_color)}; padding:10px 14px; border-radius:10px; font-weight:600;'>Botão Primário</span>
          <span style='background:{menu_color}; color:{choose_text_color(menu_color)}; padding:10px 14px; border-radius:10px; font-weight:600; border:2px solid {primary_color};'>Botão Secundário</span>
        </div>
      </div>
    </div>
    """
    st.markdown(default_preview, unsafe_allow_html=True)
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

if st.button("Salvar"):
    if selected_theme == "Custom":
        background_color = normalize_color(background_color, custom_background_color)
        secondary_color = normalize_color(secondary_color, custom_secondary_color)
        primary_color = normalize_color(primary_color, custom_primary_color)
        text_color = normalize_color(text_color, custom_text_color)
        write_theme_section({
            "base": "dark",
            "backgroundColor": background_color,
            "secondaryBackgroundColor": secondary_color,
            "primaryColor": primary_color,
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
