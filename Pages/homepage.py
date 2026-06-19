import streamlit as st
import streamlit.components.v1 as components
import os

# # # coluna_esquerda, coluna_direita = st.columns([3,1]) # Cria 2 colunas e a segunda é 50% maior que a primeira

# # # conteiner = coluna_esquerda.container(border=False)
# # # caminho_img = os.path.join("Imagens","Logo.png")
# # # conteiner.image(caminho_img) 

# # # conteiner = coluna_direita.container(border=False)
# # # with conteiner:
# # #      st.markdown('Desenvolvido por FBJ Pharma')
# # #      st.markdown(':point_right: Versão 1.0')
# # #      # Exibir empresa apenas para gerente e funcionário
# # #      if st.session_state.get("role") not in ["admin","supervisor"]:
# # #         empresa = st.session_state.get("empresa","")
# # #      else:
# # #         empresa = "FBJ Pharma"  # Exibir nome da empresa para admin e supervisor

# # #      st.markdown(
# # #      f"""
# # #      <div style="
# # #           color: orange;
# # #           font-size: 24px;
# # #           font-weight: 600;
# # #           margin-top: 5px;
# # #      ">
# # #           {empresa}
# # #      </div>
# # #      """,
# # #      unsafe_allow_html=True)
# # #      st.markdown(f'Usuário: {st.session_state.user_name}') 
# # #      st.markdown(f'Tipo de acesso: {st.session_state.role.upper()}') 


# # # if "ger_aba" in st.session_state:
# # #     st.session_state.ger_aba = "Listar"

from Pages.crud import contar_areas, contar_linhas, contar_processos, contar_equipamentos, contar_produtos
from components.top_menu import render_top_menu
from components.sidebar import render_app_sidebar

if not st.session_state.get("authenticated", False):
    st.stop()

render_app_sidebar()

# =====================================================
# CABEÇALHO
# =====================================================

st.title("🏭 FBJ Pharma")
st.caption("Sistema de Planejamento e Gestão Industrial")

# =====================================================
# EMPRESA
# =====================================================

empresa = st.session_state.get("empresa", "")

if st.session_state.get("role") not in ["admin", "supervisor"]:

    st.markdown(
        f"""
        <div style="
            font-size:22px;
            font-weight:bold;
            color:orange;
            margin-bottom:10px;
        ">
            Empresa: {empresa}
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

st.subheader("📊 Visão Geral")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "🏭 Áreas",
        total_areas
    )

with c2:
    st.metric(
        "🏗️ Linhas",
        total_linhas
    )

with c3:
    st.metric(
        "⚙️ Processos",
        total_processos
    )

with c4:
    st.metric(
        "🔧 Equipamentos",
        total_equipamentos
    )

with c5:
    st.metric(
        "📦 Produtos",
        total_produtos
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
            "Pages/areas.py",
            label="Abrir"
        )

with c2:
    with st.container(border=True):

        st.markdown("### 🏗️")
        st.markdown("**Linhas de Produção**")

        st.page_link(
            "Pages/linhas.py",
            label="Abrir"
        )
with c3:
    with st.container(border=True):

        st.markdown("### ⚙️")
        st.markdown("**Processos**")

        st.page_link(
            "Pages/processos.py",
            label="Abrir"
        )
with c4:
    with st.container(border=True):

        st.markdown("### 🔧")
        st.markdown("**Equipamentos**")

        st.page_link(
            "Pages/equipamentos.py",
            label="Abrir"
        )

st.write("")
c1, c2, c3, c4 = st.columns(4)

with c1:
    with st.container(border=True):

        st.markdown("### 📦")
        st.markdown("**Produtos (SKU)**")

        st.page_link(
            "Pages/produtos.py",
            label="Abrir"
        )
with c2:
    with st.container(border=True):

        st.markdown("### 📈")
        st.markdown("**Demandas**")

        st.page_link(
            "Pages/demandas.py",
            label="Abrir"
        )        
with c3:

    with st.container(border=True):

        st.markdown("### 📅")
        st.markdown("**Paradas Programadas**")

        st.page_link(
            "Pages/paradas.py",
            label="Abrir"
        )

with c4:
    with st.container(border=True):

        st.markdown("### 🎨")
        st.markdown("**Layout Industrial**")
        st.page_link(
            "Pages/layout.py",
            label="Abrir"
        )

# =====================================================
# ADMIN / SUPERVISOR
# =====================================================
if st.session_state.get("role") in ["admin", "supervisor"]:

    st.divider()
    st.subheader("🔐 Administração")

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):

            st.markdown("### 🏢")
            st.markdown("**Clientes**")

            st.page_link(
                "Pages/clientes.py",
                label="Abrir"
            )
    with c2:
        with st.container(border=True):

            st.markdown("### 👥")
            st.markdown("**Usuários**")

            st.page_link(
                "Pages/usuarios.py",
                label="Abrir"
            )        
