import streamlit as st
from pathlib import Path
import re

from core.database import get_supabase_client

st.set_page_config(layout="wide", page_title="FBJ Pharma")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None

# Tela de login antes da navegação principal
if not st.session_state.authenticated:
    st.title("Login")
    st.write("Informe seu usuário e senha para acessar o aplicativo.")

    with st.form("login_form"):
        username = st.text_input("Usuário", value="")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            try:
                supabase_client = get_supabase_client()
                auth = supabase_client.auth

                if hasattr(auth, "sign_in_with_password"):
                    response = auth.sign_in_with_password({
                        "email": username,
                        "password": password,
                    })
                else:
                    response = auth.sign_in(email=username, password=password)

                error = getattr(response, "error", None)
                if isinstance(response, dict) and error is None:
                    error = response.get("error")

                session = getattr(response, "session", None)
                if isinstance(response, dict) and session is None:
                    session = response.get("session")

                if error:
                    st.error("Usuário ou senha inválidos. Verifique seu login no Supabase.")
                elif session is None:
                    st.error("Falha na autenticação. Tente novamente.")
                else:
                    access_token = None
                    refresh_token = None
                    if isinstance(session, dict):
                        access_token = session.get("access_token")
                        refresh_token = session.get("refresh_token")
                        user_obj = session.get("user")
                    else:
                        access_token = getattr(session, "access_token", None)
                        refresh_token = getattr(session, "refresh_token", None)
                        user_obj = getattr(session, "user", None)

                    if access_token and refresh_token:
                        supabase_client.auth.set_session(access_token, refresh_token)
                    else:
                        st.warning("Sessão Supabase recebeu token incompleto; autenticação pode não persistir corretamente.")

                    st.session_state.authenticated = True
                    st.session_state.user = username
                    st.session_state.user_name = username
                    st.session_state.supabase_access_token = access_token
                    st.session_state.supabase_refresh_token = refresh_token
                    st.session_state.user_id = (
                        user_obj.get("id") if isinstance(user_obj, dict) else getattr(user_obj, "id", None)
                    )

                    st.write("--- DEBUG AUTENTICAÇÃO ---")
                    st.write("access_token ok:", bool(access_token))
                    st.write("refresh_token ok:", bool(refresh_token))
                    st.write("session user id:", st.session_state.user_id)
                    st.write("session object:", session)
                    st.write("supabase auth session:", supabase_client.auth.get_session())
                    st.write("--- FIM DEBUG ---")

                    #st.rerun()
            except Exception as e:
                st.error(f"Erro ao autenticar com Supabase: {e}")

    if not st.session_state.authenticated:
        st.stop()

# #import streamlit_authenticator as stauth


def read_streamlit_theme():
    config_path = Path(__file__).resolve().parent / ".streamlit" / "config.toml"
    if not config_path.exists():
        return {}
    content = config_path.read_text(encoding="utf-8")
    result = {}
    for key in ["backgroundColor", "secondaryBackgroundColor", "textColor", "primaryColor"]:
        match = re.search(rf"^{key}\s*=\s*['\"]([^'\"]+)['\"]", content, flags=re.MULTILINE)
        if match:
            result[key] = match.group(1)
    return result


theme_colors = read_streamlit_theme()
if theme_colors:
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
    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] * {
        font-size: 18px !important;
        line-height: 1.5 !important;
    }
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] h4,
    [data-testid="stAppViewContainer"] h5,
    [data-testid="stAppViewContainer"] h6 {
        font-size: 1.4em !important;
    }
    button[title="Open GitHub"] {display: none;}
    button[title="Edit this app"] {display: none;}
    /* Esconda ícones de configurações se necessário */
    [data-testid="stToolbar"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
pg = st.navigation(
    {              
        'FBJ Pharma':[st.Page('homepage.py',  title='Home',                 icon=':material/filter_alt:')],
        'Cadastros':   [
                        st.Page('clientes.py',  title='Cadastro de Clientes', icon=':material/groups:'),
                        st.Page('produtos.py',  title='Cadastro de Produtos', icon=':material/thermostat:'),
                        ],
        'Configurações':   [
                        st.Page('layout.py',      title='Layout',   icon=':material/format_paint:'),
                        ],
    }
)

pg.run()