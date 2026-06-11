import streamlit as st
import os

coluna_esquerda, coluna_direita = st.columns([3,1]) # Cria 2 colunas e a segunda é 50% maior que a primeira

conteiner = coluna_esquerda.container(border=False)
caminho_img = os.path.join("Imagens","Logo.png")
conteiner.image(caminho_img) 

conteiner = coluna_direita.container(border=False)
with conteiner:
     st.markdown('Desenvolvido por FBJ Pharma')
     st.markdown(':point_right: Versão 1.0')
     st.markdown(f'Usuário: {st.session_state.user_name}') 
     st.markdown(f'Tipo de acesso: {st.session_state.role.upper()}') 


if "ger_aba" in st.session_state:
    st.session_state.ger_aba = "Listar"