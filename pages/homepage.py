import streamlit as st
import streamlit.components.v1 as components
import os

from pages.crud import contar_areas, contar_linhas, contar_processos, contar_equipamentos, contar_produtos
from components.top_menu import render_top_menu
from components.sidebar import render_app_sidebar

if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

render_app_sidebar()

# =====================================================
# CABEÇALHO
# =====================================================

col_header_left, col_header_right = st.columns([3, 2])

with col_header_left:
    st.title("🏭 FBJ Pharma")
    st.caption("Sistema de Planejamento e Gestão Industrial")

# =====================================================
# EMPRESA
# =====================================================

empresa = st.session_state.get("empresa", "")
# print(f"Empresa: {empresa}")
# if st.session_state.get("role") not in ["admin", "supervisor"]:
with col_header_right:
    st.markdown(
        f"""
        <div style="
            width:100%;
            min-height:3.25rem;
            display:flex;
            align-items:flex-start;
            justify-content:flex-end;
            text-align:right;
            font-size:clamp(22px, 1.6vw, 30px);
            font-weight:700;
            color:orange;
            margin-top:0.2rem;
            margin-bottom:10px;
            line-height:1.2;
        ">
            {empresa}
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# =====================================================
# INDICADORES
# =====================================================
cliente_id = None

if st.session_state.get("role") not in ["admin", "supervisor"]:
    cliente_id = st.session_state.get("cliente_id")

try:

    total_areas = contar_areas(cliente_id)
    total_linhas = contar_linhas(cliente_id)
    total_processos = contar_processos(cliente_id)
    total_equipamentos = contar_equipamentos(cliente_id)
    total_produtos = contar_produtos(cliente_id)

except Exception:

    total_areas = 0
    total_linhas = 0
    total_processos = 0
    total_equipamentos = 0
    total_produtos = 0    

# =====================================================
# ADMIN / SUPERVISOR / GERENTE
# =====================================================
if st.session_state.get("role") in ["admin", "supervisor", "gerente"]:

    st.subheader("🔐 Administração")

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):

            st.markdown("### 🏢")
            st.markdown("**Clientes**")

            st.page_link(
                "pages/clientes.py",
                help='Gerencie os clientes da plataforma',
                label="Abrir"
            )
    with c2:
        with st.container(border=True):

            st.markdown("### 👥")
            st.markdown("**Usuários**")

            st.page_link(
                "pages/usuarios.py",
                help='Gerencie os responsáveis de uma empresa',
                label="Abrir"
            )

    st.divider()

# =====================================================
# ACESSOS RÁPIDOS
# =====================================================

st.subheader("🚀 Acesso Rápido")

c1, c2, c3, c4 = st.columns(4)

with c1:
    with st.container(border=True):

        st.markdown("### 🏭")
        st.markdown("**Áreas de Produção**")
        st.page_link(
            "pages/areas.py",
            help='Gerencie as áreas de produção',
            label="Abrir"
        )

with c2:
    with st.container(border=True):

        st.markdown("### 🏗️")
        st.markdown("**Linhas de Produção**")

        st.page_link(
            "pages/linhas.py",
            help='Gerencie as linhas de produção',
            label="Abrir"
        )
with c3:
    with st.container(border=True):

        st.markdown("### ⚙️")
        st.markdown("**Processos**")

        st.page_link(
            "pages/processos.py",
            help='Gerencie os processos de produção',
            label="Abrir"
        )
with c4:
    with st.container(border=True):

        st.markdown("### 🔧")
        st.markdown("**Equipamentos**")

        st.page_link(
            "pages/equipamentos.py",
            help='Gerencie os equipamentos de produção',
            label="Abrir"
        )

st.write("")
c1, c2, c3, c4 = st.columns(4)

with c1:
    with st.container(border=True):

        st.markdown("### 📦")
        st.markdown("**Produtos (SKU)**")

        st.page_link(
            "pages/produtos.py",
            help='Gerencie os produtos (SKU) da empresa',
            label="Abrir"
        )
with c2:
    with st.container(border=True):

        st.markdown("### 📈")
        st.markdown("**Demandas**")

        st.page_link(
            "pages/demandas.py",
            help='Gerencie as demandas da empresa',
            label="Abrir"
        )        
with c3:

    with st.container(border=True):

        st.markdown("### 📅")
        st.markdown("**Paradas Programadas**")

        st.page_link(
            "pages/paradas.py",
            help='Gerencie as paradas programadas da empresa',
            label="Abrir"
        )

with c4:
    with st.container(border=True):

        st.markdown("### 🎯")
        st.markdown("**Metas**")
        st.page_link(
            "pages/metas.py",
            help='Gerencie as metas da empresa',
            label="Abrir"
        )


# =====================================================
# INDICADORES
# =====================================================
st.divider()
st.subheader("📊 Visão Geral")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "🏭 Áreas",
        border=True,
        value=total_areas
    )

with c2:
    st.metric(
        "🏗️ Linhas",
        border=True,
        value=total_linhas  
    )

with c3:
    st.metric(
        "⚙️ Processos",
        border=True,
        value=total_processos
    )

with c4:
    st.metric(
        "🔧 Equipamentos",
        border=True,
        value=total_equipamentos
    )

with c5:
    st.metric(
        "📦 Produtos",
        border=True,
        value=total_produtos
    )


