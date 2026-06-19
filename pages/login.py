import streamlit as st

from core.database import get_supabase_client
from pages.theme import read_streamlit_theme
from components.session_state import ensure_session_state


def initialize_login_state():
    ensure_session_state(
        {
            "authenticated": False,
            "user": None,
            "user_name": None,
        }
    )


def resetar_tela_usuario():
    
    estados = [
        "area_cliente_selecionado",
        "area_selecionada",
        "equip_cliente_selecionado",
        "equip_selecionada",
        "linha_cliente_selecionado",
        "linha_selecionada",
        "processo_cliente_selecionado",
        "processo_selecionado",
        "produto_cliente_selecionado",
        "produto_selecionado",
        "menu_grupo",
        "pagina",
    ]

    for estado in estados:
        st.session_state.pop(estado, None)        


def get_login_card_background():
    theme_colors = read_streamlit_theme()
    return theme_colors.get("backgroundColor", "white")


def show_login_page():
    initialize_login_state()

    if st.session_state.authenticated:
        return

    login_card_bg = get_login_card_background()

    st.markdown(
        f"""
        <style>

        .stApp {{
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        }}

        .login-card {{
            background: {login_card_bg};
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
            margin-top: 40px;
        }}

        .login-title {{
            text-align: center;
            font-size: 36px;
            font-weight: 700;
            color: white;
            margin-top: 10px;
            margin-bottom: 5px;
        }}

        .login-subtitle {{
            text-align: center;
            color: #E2E8F0;
            margin-bottom: 30px;
        }}

        .stTextInput > label,
        .stTextInput > div > div > input,
        .stTextInput > div > label {{
            font-size: 18px;
        }}

        .stTextInput > div > div > input {{
            border-radius: 10px;
            height: 52px;
        }}

        .stButton > button {{
            width: 100%;
            height: 56px;
            border-radius: 10px;
            border: none;
            background-color: #2563EB;
            color: white;
            font-size: 18px;
            font-weight: 600;
        }}

        .stButton > button:hover {{
            background-color: #1D4ED8;
        }}

        header[data-testid="stHeader"] {{
            display:none;
        }}

        /* Esconder a barra lateral de navegação nas telas de login */
        div[data-testid="stSidebar"] {{
            display: none !important;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
       # st.markdown('<div class="login-card">', unsafe_allow_html=True)

        st.markdown(
            '<div class="login-title">FBJ Pharma</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="login-subtitle">Entre com suas credenciais para acessar o sistema</div>',
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            username = st.text_input(
                "E-mail",
                #placeholder="usuario@empresa.com",
                #value = 'marilia@gmail.com',
                value = 'fabio.barreto@gmail.com',
                # value = 'jose@gmail.com'
            )

            password = st.text_input(
                "Senha",
                type="password",
                #placeholder="Digite sua senha",
                # value = '123456',
                value = 'fab1234',
                # value = '123456',
                )

            submitted = st.form_submit_button("Entrar")

            if submitted:
                authenticate_user(username, password)

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


def authenticate_user(username: str, password: str):
    try:
        supabase_client = get_supabase_client()
        auth = supabase_client.auth

        if hasattr(auth, "sign_in_with_password"):
            response = auth.sign_in_with_password({
                "email": username,
                "password": password,
            })
        else:
            response = auth.sign_in(
                email=username,
                password=password,
            )

        error = getattr(response, "error", None)

        if isinstance(response, dict) and error is None:
            error = response.get("error")

        session = getattr(response, "session", None)
        if isinstance(response, dict) and session is None:
            session = response.get("session")
          

        if error:
            st.error("Usuário ou senha inválidos.")
            return

        if session is None:
            st.error("Falha na autenticação. Tente novamente.")
            return

        handle_successful_auth(session, username)

    except Exception as e:
        st.error(f"Erro ao autenticar com Supabase: {e}")


def handle_successful_auth(session, username: str):
    access_token = None
    refresh_token = None
    user_obj = None


    if isinstance(session, dict):
        access_token = session.get("access_token")
        refresh_token = session.get("refresh_token")
        user_obj = session.get("user")
    else:
        access_token = getattr(session, "access_token", None)
        refresh_token = getattr(session, "refresh_token", None)
        user_obj = getattr(session, "user", None)

  
    if access_token and refresh_token:
        supabase_client = get_supabase_client()
        supabase_client.auth.set_session(access_token, refresh_token)

    
    resetar_tela_usuario()
    st.session_state.authenticated = True
    st.session_state.user = username

    if isinstance(user_obj, dict):
        display_name = (
            user_obj.get("user_metadata", {})
            .get("display_name")
        )
    else:
        display_name = (
            getattr(user_obj, "user_metadata", {})
            .get("display_name")
            if getattr(user_obj, "user_metadata", None)
            else None
        )

    st.session_state.user_name = (
        display_name
        if display_name
        else username
    )
    st.session_state.supabase_access_token = access_token
    st.session_state.supabase_refresh_token = refresh_token
    st.session_state.user_id = (
        user_obj.get("id")
        if isinstance(user_obj, dict)
        else getattr(user_obj, "id", None)
    )

    supabase_client = get_supabase_client()

    perfil = (
        supabase_client
        .table("perfis")
        .select("role, cliente_id")
        .eq("id", st.session_state.user_id)
        .single()
        .execute()
    )

    # Valores padrão 
    st.session_state.role = "" 
    st.session_state.cliente_id = None 
    st.session_state.empresa = "FBJ Pharma" 
    st.session_state.cliente = None


    if perfil.data:
        st.session_state.role = perfil.data["role"]
        st.session_state.cliente_id = perfil.data["cliente_id"]
        # Busca os dados completos da empresa 
        if st.session_state.cliente_id:
            cliente = (
                supabase_client
                .table("clientes")
                .select("*")
                .eq("id", st.session_state.cliente_id)
                .single()
                .execute()
            )
            if cliente.data:
                st.session_state.cliente = cliente.data
                if cliente.data['empresa'] == None:
                    st.session_state.empresa = 'FBJ Pharma'
                else:
                    st.session_state.empresa = cliente.data.get("empresa","")
                
    # Após autenticação bem sucedida, liberar a exibição da navegação
    st.rerun()


