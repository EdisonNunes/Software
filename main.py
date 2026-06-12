import streamlit as st

from login import show_login_page
from theme import apply_streamlit_theme

st.set_page_config(layout="wide", page_title="FBJ Pharma")

show_login_page()
apply_streamlit_theme()


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
        }
    )

    pg.run()
