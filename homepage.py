import streamlit as st
import os


coluna_esquerda, coluna_direita = st.columns([1,1.5]) # Cria 2 colunas e a segunda é 50% maior que a primeira

coluna_esquerda.title('FM Analytics')
coluna_esquerda.markdown("##### ") # Gera espaço entre otítulo e Versão
coluna_esquerda.markdown("#### :blue-background[Versão 1.0]") 

conteiner = coluna_direita.container(border=False)
caminho_img = os.path.join("Imagens","logo.png")
conteiner.image(caminho_img) 

if "ger_aba" in st.session_state:
    st.session_state.ger_aba = "Listar"