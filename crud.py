"""
Módulo CRUD - Compatibilidade com código legado.

Este módulo mantém compatibilidade com o código existente
enquanto direciona para os novos serviços.

DEPRECATED: Use services/clientes.py e services/servicos.py
"""

import logging
import warnings
import streamlit as st
from typing import List, Dict, Any, Optional
from supabase import create_client
from config.settings import settings
from services import ClienteService, ServicoService

# Avisar sobre depreciação
warnings.warn(
    "crud.py está deprecated. Use services/clientes.py e services/servicos.py",
    DeprecationWarning,
    stacklevel=2
)

logger = logging.getLogger(__name__)

# Instâncias dos serviços
_cliente_service = None
_servico_service = None

def _get_cliente_service() -> ClienteService:
    """Obtém instância do ClienteService."""
    global _cliente_service
    if _cliente_service is None:
        _cliente_service = ClienteService()
    return _cliente_service

def _get_servico_service() -> ServicoService:
    """Obtém instância do ServicoService."""
    global _servico_service
    if _servico_service is None:
        _servico_service = ServicoService()
    return _servico_service

# =====================================================
# CLIENTES - Funções de compatibilidade
# =====================================================

def listar_clientes(filtro_empresa: str = "") -> List[Dict[str, Any]]:
    """
    Lista clientes (compatibilidade).

    DEPRECATED: Use ClienteService.listar()
    """
    try:
        return _get_cliente_service().listar(filtro_empresa)
    except Exception as e:
        logger.error(f"Erro em listar_clientes: {e}")
        return []

def listar_todos_dados_clientes() -> List[Dict[str, Any]]:
    """
    Lista todos os dados de clientes (compatibilidade).

    DEPRECATED: Use ClienteService.listar_todos()
    """
    try:
        return _get_cliente_service().listar_todos()
    except Exception as e:
        logger.error(f"Erro em listar_todos_dados_clientes: {e}")
        return []

def incluir_cliente(dados: Dict[str, Any]) -> None:
    """
    Inclui cliente (compatibilidade).

    DEPRECATED: Use ClienteService.criar()
    """
    try:
        _get_cliente_service().criar(dados)
    except Exception as e:
        logger.error(f"Erro em incluir_cliente: {e}")
        raise

def alterar_cliente(id_cliente: int, dados: Dict[str, Any]) -> None:
    """
    Altera cliente (compatibilidade).

    DEPRECATED: Use ClienteService.atualizar()
    """
    try:
        _get_cliente_service().atualizar(id_cliente, dados)
    except Exception as e:
        logger.error(f"Erro em alterar_cliente: {e}")
        raise

def excluir_cliente(id_cliente: int) -> None:
    """
    Exclui cliente (compatibilidade).

    DEPRECATED: Use ClienteService.excluir()
    """
    try:
        _get_cliente_service().excluir(id_cliente)
    except Exception as e:
        logger.error(f"Erro em excluir_cliente: {e}")
        raise

# =====================================================
# SERVIÇOS - Funções de compatibilidade
# =====================================================

def listar_servicos(filtro_descricao: str = "") -> List[Dict[str, Any]]:
    """
    Lista serviços (compatibilidade).

    DEPRECATED: Use ServicoService.listar()
    """
    try:
        return _get_servico_service().listar(filtro_descricao)
    except Exception as e:
        logger.error(f"Erro em listar_servicos: {e}")
        return []

def listar_todos_dados_servicos() -> List[Dict[str, Any]]:
    """
    Lista todos os dados de serviços (compatibilidade).

    DEPRECATED: Use ServicoService.listar_todos()
    """
    try:
        return _get_servico_service().listar_todos()
    except Exception as e:
        logger.error(f"Erro em listar_todos_dados_servicos: {e}")
        return []

def incluir_servico(dados: Dict[str, Any]) -> None:
    """
    Inclui serviço (compatibilidade).

    DEPRECATED: Use ServicoService.criar()
    """
    try:
        _get_servico_service().criar(dados)
    except Exception as e:
        logger.error(f"Erro em incluir_servico: {e}")
        raise

def alterar_servico(id_servico: int, dados: Dict[str, Any]) -> None:
    """
    Altera serviço (compatibilidade).

    DEPRECATED: Use ServicoService.atualizar()
    """
    try:
        _get_servico_service().atualizar(id_servico, dados)
    except Exception as e:
        logger.error(f"Erro em alterar_servico: {e}")
        raise

def excluir_servico(id_servico: int) -> None:
    """
    Exclui serviço (compatibilidade).

    DEPRECATED: Use ServicoService.excluir()
    """
    try:
        _get_servico_service().excluir(id_servico)
    except Exception as e:
        logger.error(f"Erro em excluir_servico: {e}")
        raise

def verificar_uso_servico(id_servico: int) -> List[Dict[str, Any]]:
    """
    Verifica uso do serviço (compatibilidade).

    DEPRECATED: Use ServicoService.verificar_uso()
    """
    try:
        return _get_servico_service().verificar_uso(id_servico)
    except Exception as e:
        logger.error(f"Erro em verificar_uso_servico: {e}")
        return []

# =====================================================
# LEGACY - Manter compatibilidade
# =====================================================

class SupabaseProxy:
    """Proxy para manter compatibilidade com código legado."""

    def __init__(self):
        """Inicializa sem criar cliente imediatamente."""
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            config = settings.get_supabase_config()
            self._client = create_client(config["url"], config["key"])

            access_token = st.session_state.get("supabase_access_token")
            refresh_token = st.session_state.get("supabase_refresh_token")
            if access_token and refresh_token:
                try:
                    self._client.auth.set_session(access_token, refresh_token)
                except Exception:
                    logger.warning(
                        "Não foi possível restaurar sessão Supabase no proxy crud"
                    )

    def __getattr__(self, name):
        """Delegar chamadas para o cliente Supabase real."""
        self._ensure_client()
        return getattr(self._client, name)

# Instância global para compatibilidade
supabase = SupabaseProxy()

# Funções de propostas (mantidas por enquanto)
def criar_proposta(dados):
    """Criar proposta - TODO: refatorar."""
    logger.warning("criar_proposta não implementada na nova arquitetura")
    return None

def atualizar_proposta(id_proposta, dados):
    """Atualizar proposta - TODO: refatorar."""
    logger.warning("atualizar_proposta não implementada na nova arquitetura")
    return None

def excluir_proposta(id_proposta):
    """Excluir proposta - TODO: refatorar."""
    logger.warning("excluir_proposta não implementada na nova arquitetura")
    return None

def buscar_propostas(filtro=""):
    """Buscar propostas - TODO: refatorar."""
    logger.warning("buscar_propostas não implementada na nova arquitetura")
    return []

def adicionar_item(dados):
    """Adicionar item - TODO: refatorar."""
    logger.warning("adicionar_item não implementada na nova arquitetura")
    return None

def buscar_itens(id_proposta):
    """Buscar itens - TODO: refatorar."""
    logger.warning("buscar_itens não implementada na nova arquitetura")
    return []

def atualizar_item(id_item, dados):
    """Atualizar item - TODO: refatorar."""
    logger.warning("atualizar_item não implementada na nova arquitetura")
    return None

def excluir_item(id_item):
    """Excluir item - TODO: refatorar."""
    logger.warning("excluir_item não implementada na nova arquitetura")
    return None

# ####################################################
# CLIENTES  - TABELA CLIENTES
# create table public.clientes (
#   id uuid not null default gen_random_uuid (),
#   created_at timestamp with time zone not null default now(),
#   empresa text not null,
#   cnpj text not null,
#   cep text null,
#   endereco text null,
#   cidade text not null,
#   uf text not null,
#   contato text null,
#   telefone text null,
#   email text not null,
#   status boolean not null default true,
#   constraint clientes_pkey primary key (id),
#   constraint clientes_cnpj_key unique (cnpj)
# ) TABLESPACE pg_default;
# ####################################################

def listar_clientes(filtro_empresa=""):
    query = supabase.table("clientes").select("id, empresa, cidade, telefone, contato, email")
    if filtro_empresa:
        query = query.filter("empresa", "ilike", f"%{filtro_empresa}%")
    query = query.order("empresa", desc=False)
    response = query.execute()
    # print(response.data)
    return response.data

def listar_todos_dados_clientes():
    query = supabase.table("clientes").select("*").order("empresa", desc=False)
    response = query.execute()
    print(response.data)
    return response.data
def incluir_cliente(dados):
    existe = supabase.table("clientes").select("*") \
        .eq("empresa", dados["empresa"]).eq("cidade", dados["cidade"]).execute()
    if existe.data:
        raise ValueError("Já existe um cliente com essa empresa e cidade.")
    # dados["id"] = uuid.uuid4().int >> 64
    supabase.table("clientes").insert(dados).execute()

def alterar_cliente(id, dados):
    supabase.table("clientes").update(dados).eq("id", id).execute()

def excluir_cliente(id):
    supabase.table("clientes").delete().eq("id", id).execute()

# ####################################################
# PRODUTOS  - TABELA PRODUTOS
# create table public.produtos (
#   id uuid not null default gen_random_uuid (),
#   created_at timestamp with time zone not null default now(),
#   cliente_id uuid null default gen_random_uuid (),
#   codigo text not null,
#   descricao text not null,
#   familia text null,
#   area_produtiva text null,
#   area_embalagem text null,
#   lote_padrao numeric null,
#   area_rota text null,
#   equipamento text null,
#   classificacao text null,
#   tempo_ciclo numeric null,
#   constraint produtos_pkey primary key (id),
#   constraint produtos_cliente_id_fkey foreign KEY (cliente_id) references clientes (id) on update CASCADE on delete CASCADE
# ) TABLESPACE pg_default;
# ####################################################    
def listar_produtos(filtro_produto=""):
    query = supabase.table("produtos").select("id, codigo, descricao, familia, area_produtiva, area_embalagem, lote_padrao, area_rota, equipamento, classificacao, tempo_ciclo")
    if filtro_produto:
        query = query.filter("cliente_id", "eq", filtro_produto)
    query = query.order("descricao", desc=False)
    response = query.execute()
    return response.data

def listar_todos_dados_produtos():
    query = supabase.table("produtos").select("*").order("descricao", desc=False)
    response = query.execute()
    # print(response.data)
    return response.data

def incluir_produto(dados):
    existe = supabase.table("produtos").select("*") \
        .eq("descricao", dados["descricao"]).execute()
    #   .eq("empresa", dados["empresa"]).eq("cidade", dados["cidade"]).execute()
    if existe.data:
        raise ValueError("Já existe um produto com essa descricao.")
    supabase.table("produtos").insert(dados).execute()

def alterar_produto(id, dados):
    supabase.table("produtos").update(dados).eq("id", id).execute()

def excluir_produto(id):
    supabase.table("produtos").delete().eq("id", id).execute()

  

def ComboBoxClientes():
    response = supabase.table("clientes").select("id, empresa, cidade").order('empresa').execute()
    # Verificar se a resposta tem dados
    if response.data and isinstance(response.data, list):
        clientes = response.data
        opcoes_combobox = [
            f"{cliente['empresa']} - {cliente['cidade']}" for cliente in clientes
        ]
        # print(opcoes_combobox)
    else:
        st.error("Erro ao carregar os dados dos clientes.")
        clientes = []
        opcoes_combobox = []
    return opcoes_combobox 

# ####################################################
# PROPOSTAS  - TABELA PROPOSTAS
# create table public.propostas (
#   id_proposta integer generated by default as identity not null,
#   id_cliente integer not null,
#   num_proposta text not null,
#   empresa text not null,
#   cnpj text not null,
#   endereco text not null,
#   cidade text not null,
#   uf text not null,
#   telefone text not null,
#   email text not null,
#   contato text not null,
#   status_rel_01 text null,
#   local_realizacao text null,
#   dt_agendada_01 date null,
#   dt_emissao_rel_01 date null,
#   motivo_cancelamento text null,
#   data_emissao date not null,
#   validade text not null,
#   cond_pagamento text not null,
#   referencia text null,
#   total_qtd numeric(12, 2) null default 0,
#   total_valor numeric(12, 2) null default 0,
#   created_at timestamp without time zone null default now(),
#   constraint propostas_pkey1 primary key (id_proposta),
#   constraint propostas_num_proposta_key unique (num_proposta),
#   constraint fk_proposta_cliente foreign KEY (id_cliente) references clientes (id) on delete RESTRICT
# ) TABLESPACE pg_default;

# create index IF not exists idx_propostas_cliente on public.propostas using btree (id_cliente) TABLESPACE pg_default;

# create trigger trg_snapshot_cliente BEFORE INSERT on propostas for EACH row
# execute FUNCTION fn_snapshot_cliente ();
# ####################################################  
def criar_proposta(dados: dict) -> int:
    res = supabase.table("propostas").insert(dados).execute()
    return res.data[0]["id_proposta"]

def atualizar_proposta(id_proposta: int, dados: dict):
    supabase.table("propostas").update(dados).eq("id_proposta", id_proposta).execute()

def excluir_proposta(id_proposta: int):
    supabase.table("propostas").delete().eq("id_proposta", id_proposta).execute()

def buscar_propostas(filtro: str = ""):
    q = (
        supabase
        .table("propostas")
        .select("*")
        # .order("data_emissao", desc=True)  # 🔥 ordem pela data (mais recente primeiro)
        .order("num_proposta", desc=True)  # 🔥 ordem pela data (mais recente primeiro)
        .order("id_proposta", desc=True)   # 🔒 desempate seguro
    )
    if filtro:
        q = q.ilike("num_proposta", f"%{filtro}%")
    return q.execute().data

# ####################################################
# ITENS DA PROPOSTA  - TABELA ITENS_PROPOSTA
# create table public.itens_proposta (
#   id_item_prop integer generated by default as identity not null,
#   id_proposta integer not null,
#   id_servico integer not null,
#   codigo_servico text not null,
#   descricao_servico text not null,
#   prazo_ddl text not null,
#   qtd numeric(12, 2) not null default 1,
#   preco_unitario numeric(12, 2) not null,
#   desconto numeric(12, 2) not null default 0,
#   total_item numeric GENERATED ALWAYS as (((qtd * preco_unitario) - desconto)) STORED (12, 2) null,
#   constraint itens_proposta_pkey primary key (id_item_prop),
#   constraint fk_item_proposta foreign KEY (id_proposta) references propostas (id_proposta) on delete CASCADE,
#   constraint fk_item_servico foreign KEY (id_servico) references servicos (id_servico) on delete RESTRICT
# ) TABLESPACE pg_default;
# create index IF not exists idx_itens_proposta_proposta on public.itens_proposta using btree (id_proposta) TABLESPACE pg_default;
# create index IF not exists idx_itens_proposta_servico on public.itens_proposta using btree (id_servico) TABLESPACE pg_default;
# create trigger trg_totais_proposta
# after INSERT
# or DELETE
# or
# update on itens_proposta for EACH row
# execute FUNCTION atualizar_totais_proposta ();
# ####################################################  
def adicionar_item(id_proposta: int, item: dict):
    item["id_proposta"] = id_proposta
    supabase.table("itens_proposta").insert(item).execute()

def atualizar_item(id_item_prop: int, dados: dict):
    supabase.table("itens_proposta").update(dados).eq("id_item_prop", id_item_prop).execute()

def excluir_item(id_item_prop: int):
    supabase.table("itens_proposta").delete().eq("id_item_prop", id_item_prop).execute()

def buscar_itens(id_proposta: int):
    return (
        supabase.table("itens_proposta")
        .select("*")
        .eq("id_proposta", id_proposta)
        .execute()
        .data
    )
# create table public.sequencia (
#   id bigint not null,
#   last_proposta text not null,
#   constraint sequencia_pkey primary key (id)
# ) TABLESPACE pg_default;
def ler_last_proposta() -> str:
    """
    Lê o campo 'last_proposta' do registro com id=1 na tabela 'sequencia'.
    """
    try:
        response = supabase.table("sequencia").select("last_proposta").eq("id", 1).execute()
        
        if response.data:
            return response.data[0]["last_proposta"]
        else:
            # Caso a tabela esteja vazia, retorna um valor padrão ou levanta erro
            return "C-2026001" 
    except Exception as e:
        st.error(f"Erro ao ler do Supabase: {e}")
        return None
    
def atualizar_last_proposta(nova_proposta: str):
    """
    Atualiza o campo 'last_proposta' do registro com id=1 na tabela 'sequencia'.
    """
    try:
        response = supabase.table("sequencia").update({"last_proposta": nova_proposta}).eq("id", 1).execute()
        return response
    except Exception as e:
        st.error(f"Erro ao atualizar o Supabase: {e}")
        return None    