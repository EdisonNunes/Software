from datetime import date

import pandas as pd
import streamlit as st

from components.page_banner import render_cliente_banner, render_page_title_banner
from components.session_state import ensure_session_state
from components.sidebar import render_app_sidebar
from components.top_menu import render_top_menu
from pages.crud import listar_clientes
from services.servicos import gerar_ordens, oee_ordem, replanejar, simular


if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

render_app_sidebar()
render_top_menu()
render_page_title_banner("Planejamento MES", icon_html="&#129504;")

ensure_session_state(
    {
        "pln_cliente_selecionado": None,
        "pln_cliente_id_selecionado": "",
        "pln_cliente_pagina": 0,
        "pln_busca_cliente": "",
        "pln_aba": "Executar",
        "pln_ordem_id": "",
        "pln_ultima_resposta": None,
        "pln_oee_resultado": None,
        "pln_oee_consultado": False,
    }
)

if st.session_state.get("role") not in ["admin", "supervisor"]:
    if st.session_state.pln_cliente_selecionado is None and st.session_state.get("cliente"):
        st.session_state.pln_cliente_selecionado = st.session_state.cliente

PAGE_SIZE = 10


def _cliente_id_selecionado(cliente: dict | None):
    if not cliente:
        return None
    return (
        cliente.get("id")
        or cliente.get("cliente_id")
        or cliente.get("id_cliente")
    )


def _render_seletor_cliente() -> dict | None:
    if st.session_state.get("role") not in ["admin", "supervisor"]:
        cliente_padrao = st.session_state.get("cliente") or st.session_state.pln_cliente_selecionado
        if cliente_padrao:
            cliente_id_padrao = _cliente_id_selecionado(cliente_padrao) or st.session_state.get("cliente_id")
            st.session_state.pln_cliente_id_selecionado = str(cliente_id_padrao or "")
        return cliente_padrao

    busca = st.text_input("Buscar cliente", st.session_state.pln_busca_cliente)
    if busca != st.session_state.pln_busca_cliente:
        st.session_state.pln_busca_cliente = busca
        st.session_state.pln_cliente_pagina = 0
        st.rerun()

    clientes = listar_clientes(filtro_empresa=st.session_state.pln_busca_cliente)
    total = len(clientes)
    inicio = st.session_state.pln_cliente_pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE

    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} clientes")

    if clientes:
        clientes_paginados = clientes[inicio:fim]
        df_clientes = pd.DataFrame(clientes_paginados).copy()
        df_clientes["Selecionar"] = False

        selecao_cli = st.data_editor(
            df_clientes[["Selecionar", "empresa", "cidade", "telefone", "contato"]].reset_index(drop=True),
            hide_index=True,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Selecionar", help="Marque para selecionar"),
                "empresa": st.column_config.TextColumn("Empresa"),
                "cidade": st.column_config.TextColumn("Cidade"),
                "telefone": st.column_config.TextColumn("Telefone"),
                "contato": st.column_config.TextColumn("Contato"),
            },
            key="planejamento_grid_clientes",
        )

        selecionados_cli = selecao_cli[selecao_cli["Selecionar"] == True]
        if len(selecionados_cli) == 1:
            idx = selecionados_cli.index[0]
            if idx < len(clientes_paginados):
                cliente_selecionado = clientes_paginados[idx]
                st.session_state.pln_cliente_selecionado = cliente_selecionado
                st.session_state.pln_cliente_id_selecionado = str(_cliente_id_selecionado(cliente_selecionado) or "")
        elif len(selecionados_cli) > 1:
            st.error("Selecione apenas 1 cliente por vez.")

    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    if col_pag1.button("⬅️", disabled=st.session_state.pln_cliente_pagina <= 0):
        st.session_state.pln_cliente_pagina -= 1
        st.rerun()
    col_pag2.write(f"Página {st.session_state.pln_cliente_pagina + 1} de {total_paginas}")
    if col_pag3.button("➡️", disabled=(st.session_state.pln_cliente_pagina + 1) >= total_paginas):
        st.session_state.pln_cliente_pagina += 1
        st.rerun()

    return st.session_state.pln_cliente_selecionado


cliente = _render_seletor_cliente()
cliente_id = st.session_state.get("pln_cliente_id_selecionado", "")

if not cliente_id:
    cliente_id = str(_cliente_id_selecionado(cliente) or "")
    st.session_state.pln_cliente_id_selecionado = cliente_id

if cliente:
    render_cliente_banner(cliente, 0, total_label="Planejamento")

st.markdown(
    """
    <div style="
        padding: 14px 18px;
        border-radius: 14px;
        margin: 0.5rem 0 1rem 0;
        border: 1px solid rgba(148, 163, 184, 0.30);
        background: linear-gradient(135deg, rgba(37,99,235,0.08), rgba(14,165,233,0.04));
    ">
        <strong>Operações do Planejamento MES</strong><br>
        Gere ordens otimizadas, replaneje a produção ou simule cenários para a data selecionada.
    </div>
    """,
    unsafe_allow_html=True,
)
data_producao = st.date_input("Data de Produção", value=date.today(), )

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚀 Gerar Ordens", width='stretch', disabled=not cliente_id):
        try:
            resposta = gerar_ordens(cliente_id, data_producao)
            quantidade = len(resposta.data) if getattr(resposta, "data", None) else 0
            st.session_state.pln_ultima_resposta = resposta.data if getattr(resposta, "data", None) else []
            st.success(f"Ordens geradas com sucesso! {quantidade} registro(s) retornado(s).")
            if getattr(resposta, "data", None):
                st.dataframe(pd.DataFrame(resposta.data), width='stretch')
        except Exception as e:
            st.session_state.pln_ultima_resposta = []
            st.error(f"Erro ao gerar ordens: {e}")

with col2:
    if st.button("🔁 Replanejar", width='stretch', disabled=not cliente_id):
        try:
            resposta = replanejar(cliente_id, data_producao)
            quantidade = len(resposta.data) if getattr(resposta, "data", None) else 0
            st.session_state.pln_ultima_resposta = resposta.data if getattr(resposta, "data", None) else []
            st.warning(f"Replanejamento executado! {quantidade} registro(s) retornado(s).")
            if getattr(resposta, "data", None):
                st.dataframe(pd.DataFrame(resposta.data), width='stretch')
        except Exception as e:
            st.session_state.pln_ultima_resposta = []
            st.error(f"Erro ao replanejar: {e}")

with col3:
    if st.button("📊 Simular", width='stretch', disabled=not cliente_id):
        try:
            print(f"Simulando para cliente_id={cliente_id}, data_producao={data_producao}")

            resposta = simular(cliente_id, data_producao)
            print(f"Resposta da simulação: {resposta}")
            st.session_state.pln_ultima_resposta = resposta.data if getattr(resposta, "data", None) else []
            st.success("Simulação executada com sucesso!")
            if getattr(resposta, "data", None):
                st.dataframe(pd.DataFrame(resposta.data), width='stretch')
            else:
                st.info("A função não retornou linhas para exibição.")
        except Exception as e:
            st.session_state.pln_ultima_resposta = []
            st.error(f"Erro ao simular: {e}")


st.divider()
st.subheader("Resultado da Última Operação")
ultima_resposta = st.session_state.get("pln_ultima_resposta")
if ultima_resposta:
    st.dataframe(pd.DataFrame(ultima_resposta), width='stretch')
else:
    st.info("Sem dados retornados pela última operação.")


st.subheader("OEE por Ordem")
col_ordem, col_exec = st.columns([2, 1])
with col_ordem:
    ordem_id = st.text_input("ID da Ordem", value=st.session_state.get("pln_ordem_id", ""))
with col_exec:
    if st.button("Calcular OEE", width='stretch', disabled=not ordem_id.strip()):
        try:
            st.session_state.pln_ordem_id = ordem_id.strip()
            resposta_oee = oee_ordem(ordem_id.strip())
            st.session_state.pln_oee_consultado = True
            st.session_state.pln_oee_resultado = resposta_oee.data if getattr(resposta_oee, "data", None) else []
            st.success("Cálculo de OEE executado com sucesso!")
        except Exception as e:
            st.session_state.pln_oee_consultado = True
            st.session_state.pln_oee_resultado = []
            st.error(f"Erro ao calcular OEE: {e}")

if st.session_state.get("pln_oee_consultado"):
    if st.session_state.get("pln_oee_resultado"):
        st.dataframe(pd.DataFrame(st.session_state.pln_oee_resultado), width='stretch')
    else:
        st.info("Sem dados retornados pelo cálculo de OEE.")
