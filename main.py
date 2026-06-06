import streamlit as st

from login import show_login_page
from theme import apply_streamlit_theme

st.set_page_config(layout="wide", page_title="FBJ Pharma")

show_login_page()
apply_streamlit_theme()

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