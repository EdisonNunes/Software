import streamlit as st

from login import show_login_page
from theme import apply_streamlit_theme
from crud import supabase

def logout():

    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    # Limpa as informações do usuário mas mantém a flag que indica
    # que a aplicação deve mostrar apenas a tela de login.
    for chave in list(st.session_state.keys()):
        if chave not in ("show_login_only",):
            del st.session_state[chave]

    st.session_state.show_login_only = True

    st.rerun()


# Define estado inicial da sidebar com base na flag de mostrar só login
initial_sidebar = (
    "collapsed" if st.session_state.get("show_login_only") else "expanded"
)
st.set_page_config(layout="wide", page_title="FBJ Pharma", initial_sidebar_state=initial_sidebar)

show_login_page()

# Se a flag indicar que deve mostrar somente o login, interrompe aqui
if st.session_state.get("show_login_only") or not st.session_state.get("user_name"):
    st.stop()

apply_streamlit_theme()

with st.sidebar:
    if st.session_state.get("user_name"):
        st.caption(f"Usuário: {st.session_state.user_name}"
    )

    if st.button("🚪 Logout", use_container_width=True):
        logout()
  

if st.session_state.role == "supervisor" or st.session_state.role == "admin":
        
    pg = st.navigation(
        {              
            'FBJ Pharma':[st.Page('homepage.py',  title='Home',                 icon=':material/filter_alt:')],
            'Planejamento': [
                            st.Page('demandas.py',  title='Demanda', icon=':material/view_timeline:'),
                            st.Page('paradas.py',  title='Paradas Programadas', icon=':material/calendar_month:'),
                            ],
        'Cadastros Gerais': [
                            st.Page('areas.py',   title='Áreas de Produção',  icon=':material/activity_zone:'),
                            st.Page('equipamentos.py',  title='Equipamentos', icon=':material/precision_manufacturing:'),
                            ],                
            'Supervisor':   [
                            st.Page('clientes.py',  title='Cadastro de Clientes', icon=':material/factory:'),
                            st.Page('usuarios.py',  title='Cadastro de Usuários', icon=':material/groups:'),
                            ],
        'Configurações':   [
                            st.Page('produtos.py',  title='Cadastro SKU', icon=':material/thermostat:'),
                            st.Page('layout.py',    title='Layout',       icon=':material/format_paint:'),
                            ],
        }
    )

    pg.run()
else:
    pg = st.navigation(
        {              
            'FBJ Pharma':[st.Page('homepage.py',  title='Home',                 icon=':material/filter_alt:')],
            'Planejamento': [
                            st.Page('demandas.py',  title='Demanda', icon=':material/view_timeline:'),
                            st.Page('paradas.py',  title='Paradas Programadas', icon=':material/calendar_month:'),
                            ],
        'Cadastros Gerais': [
                            st.Page('areas.py',   title='Áreas de Produção',  icon=':material/activity_zone:'),
                            st.Page('equipamentos.py',  title='Equipamentos', icon=':material/precision_manufacturing:'),
                            ],                
        'Configurações':   [
                            st.Page('produtos.py',  title='Cadastro SKU', icon=':material/thermostat:'),
                            st.Page('layout.py',    title='Layout',       icon=':material/format_paint:'),
                            ],
        }, position="sidebar"
    )

    pg.run()
