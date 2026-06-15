"""
Módulo CRUD - Compatibilidade com código legado.

Este módulo mantém compatibilidade com o código existente
enquanto direciona para os novos serviços.

DEPRECATED: Use services/clientes.py e services/servicos.py
"""

import logging
from urllib import response
import warnings
import streamlit as st
from typing import List, Dict, Any, Optional
from supabase import create_client
from config.settings import settings
from services import ClienteService, ServicoService

# # Avisar sobre depreciação
# warnings.warn(
#     "crud.py está deprecated. Use services/clientes.py e services/servicos.py",
#     DeprecationWarning,
#     stacklevel=2
# )

logger = logging.getLogger(__name__)

# Instâncias dos serviços
_cliente_service = None
_servico_service = None

PERFIS_LABEL = {
    "admin": "Admin",
    "supervisor": "Supervisor",
    "gerente": "Gerente",
    "funcionario": "Funcionário"
}

PERFIS_VALOR = {
    "Admin": "admin",
    "Supervisor": "supervisor",
    "Gerente": "gerente",
    "Funcionário": "funcionario"
}

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

# =====================================================
# SUPABASE ADMIN
# =====================================================

def get_supabase_admin():
    config = settings.get_supabase_config()

    return create_client(
        config["url"],
        config["service_role_key"]  # SUPABASE_SERVICE_ROLE_KEY
    )
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

# | Perfil      | Consultar          | Incluir | Alterar | Excluir |
# | ----------- | ------------------ | ------- | ------- | ------- |
# | admin       | Todos os clientes  | ✅       | ✅       | ✅       |
# | supervisor  | Todos os clientes  | ✅       | ✅       | ✅       |
# | gerente     | Apenas sua empresa | ❌       | ❌       | ❌       |
# | funcionario | Apenas sua empresa | ❌       | ❌       | ❌       |
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
    # print(response.data)
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
#   tempo_ciclo numeric null,
#   constraint produtos_pkey primary key (id),
#   constraint produtos_cliente_id_fkey foreign KEY (cliente_id) references clientes (id) on update CASCADE on delete CASCADE
# ) TABLESPACE pg_default;
# ####################################################    
def listar_produtos(filtro_produto=""):
    # print("Filtro de produto recebido:", filtro_produto)

    query = supabase.table("produtos").select("id, codigo, descricao, familia, area_produtiva, area_embalagem, lote_padrao, area_rota, equipamento, tempo_ciclo")
    
    # Apenas Admin/Supervisor terão acesso a outras empresas,
    # pois a própria RLS permitirá.
    #     
    if filtro_produto:
        query = query.filter("cliente_id", "eq", filtro_produto)
    query = query.order("descricao", desc=False)
    response = query.execute()
    # print("Resposta da consulta de produtos:", response.data)
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
# USUÁRIOS
# auth.users + public.perfis
# ####################################################

def listar_usuarios(cliente_id):

    try:

        admin = get_supabase_admin()

        response = (
            admin
            .table("perfis")
            .select("""
                id,
                role,
                cliente_id
            """)
            .eq("cliente_id", cliente_id)
            .order("role")
            .execute()
        )

        usuarios = []

        for perfil in response.data:

            try:

                user = admin.auth.admin.get_user_by_id(
                    perfil["id"]
                )

                usuarios.append({
                    "id": perfil["id"],
                    "cliente_id": perfil["cliente_id"],
                    "nome": (
                        user.user.user_metadata.get(
                            "display_name",
                            ""
                        )
                        if user.user.user_metadata
                        else ""
                    ),
                    "email": user.user.email,
                    "tipo": PERFIS_LABEL.get(
                        perfil["role"],
                        perfil["role"]
                    )
                })

            except Exception as e:
                logger.error(
                    f"Erro ao obter usuário "
                    f"{perfil['id']}: {e}"
                )

        return usuarios

    except Exception as e:
        logger.error(
            f"Erro ao listar usuários: {e}"
        )
        return []

def incluir_usuario(
    nome,
    email,
    senha,
    tipo,
    cliente_id
):

    admin = get_supabase_admin()

    if tipo not in [
        "gerente",
        "funcionario"
    ]:
        raise ValueError(
            "Tipo de usuário inválido."
        )

    usuario = admin.auth.admin.create_user(
        {
            "email": email,
            "password": senha,
            "email_confirm": True,
            "user_metadata": {
                "display_name": nome
            }
        }
    )

    user_id = usuario.user.id

    resultado = (
        admin
        .table("perfis")
        .update(
            {
                "role": tipo,
                "cliente_id": cliente_id
            }
        )
        .eq("id", user_id)
        .execute()
    )

    if not resultado.data:
        raise Exception(
            "Perfil não encontrado "
            "após criação do usuário."
        )

    return True


def alterar_usuario(
    user_id,
    nome,
    tipo
):

    admin = get_supabase_admin()

    if tipo not in [
        "gerente",
        "funcionario"
    ]:
        raise ValueError(
            "Tipo de usuário inválido."
        )

    admin.auth.admin.update_user_by_id(
        user_id,
        {
            "user_metadata": {
                "display_name": nome
            }
        }
    )

    resultado = (
        admin
        .table("perfis")
        .update(
            {
                "role": tipo
            }
        )
        .eq("id", user_id)
        .execute()
    )

    if not resultado.data:
        raise Exception(
            "Usuário não encontrado."
        )

    return True

def excluir_usuario(user_id):

    admin = get_supabase_admin()

    try:

        admin.auth.admin.delete_user(
            user_id
        )

        return True

    except Exception as e:

        logger.error(
            f"Erro ao excluir usuário: {e}"
        )

        return False
# ============================================================================================
#  create table public.areas (
#   id uuid not null default gen_random_uuid (),
#   created_at timestamp with time zone not null default now(),
#   cliente_id uuid not null,
#   codigo text not null,
#   descricao text not null,
#   constraint areas_pkey primary key (id),
#   constraint areas_cliente_id_fkey foreign KEY (cliente_id) references clientes (id) on update CASCADE on delete CASCADE
# ) TABLESPACE pg_default;
# create index IF not exists idx_areas_cliente_id on public.areas using btree (cliente_id) TABLESPACE pg_default;
# create index IF not exists idx_areas_codigo on public.areas using btree (codigo) TABLESPACE pg_default;
# create index IF not exists idx_areas_descricao on public.areas using btree (descricao) TABLESPACE pg_default;

def listar_areas(cliente_id=""):
    query = (
        supabase
        .table("areas")
        .select(
            """
            id,
            codigo,
            descricao,
            cliente_id
            """
        )
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.order("descricao", desc=False)

    response = query.execute()

    return response.data

def listar_todos_dados_areas(cliente_id=""):
    query = (
        supabase
        .table("areas")
        .select("*")
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.order("descricao", desc=False)

    response = query.execute()

    return response.data

def incluir_area(
    codigo,
    descricao,
    cliente_id
):
    response = (
        supabase
        .table("areas")
        .insert(
            {
                "codigo": codigo,
                "descricao": descricao,
                "cliente_id": cliente_id
            }
        )
        .execute()
    )

    return response.data

def alterar_area(
    area_id,
    codigo,
    descricao
):
    response = (
        supabase
        .table("areas")
        .update(
            {
                "codigo": codigo,
                "descricao": descricao
            }
        )
        .eq("id", area_id)
        .execute()
    )

    return response.data

def excluir_area(area_id):
    response = (
        supabase
        .table("areas")
        .delete()
        .eq("id", area_id)
        .execute()
    )

    return response.data

def verificar_uso_area(area_id):
    try:

        response = (
            supabase
            .table("produtos")
            .select("id")
            .eq("area_id", area_id)
            .limit(1)
            .execute()
        )

        return len(response.data) > 0

    except Exception:
        return False
# ============================================================================================
# create table public.equipamentos (
#   id uuid not null default gen_random_uuid (),
#   created_at timestamp with time zone not null default now(),
#   cliente_id uuid null,
#   codigo text not null,
#   descricao text not null,
#   constraint equipamentos_pkey primary key (id),
#   constraint equipamentos_cliente_id_fkey foreign KEY (cliente_id) references clientes (id) on update CASCADE on delete CASCADE
# ) TABLESPACE pg_default;
# create index IF not exists idx_equipamentos_cliente_id on public.equipamentos using btree (cliente_id) TABLESPACE pg_default;
# create index IF not exists idx_equipamentos_descricao on public.equipamentos using btree (descricao) TABLESPACE pg_default;
# create unique INDEX IF not exists idx_equipamentos_cliente_codigo on public.equipamentos using btree (cliente_id, codigo) TABLESPACE pg_default;

def listar_equipamentos(cliente_id=""):
    query = (
        supabase
        .table("equipamentos")
        .select(
            """
            id,
            codigo,
            descricao,
            classif,
            cliente_id
            """
        )
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.order("descricao", desc=False)

    response = query.execute()

    return response.data

def listar_todos_dados_equipamentos(cliente_id=""):
    query = (
        supabase
        .table("equipamentos")
        .select("*")
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.order("descricao", desc=False)

    response = query.execute()

    return response.data

def incluir_equipamento(
    codigo,
    descricao,
    classif,
    cliente_id
):
    response = (
        supabase
        .table("equipamentos")
        .insert(
            {
                "codigo": codigo,
                "descricao": descricao,
                "classif": classif,
                "cliente_id": cliente_id
            }
        )
        .execute()
    )

    return response.data

def alterar_equipamento(
    equipamento_id,
    codigo,
    classif,
    descricao
):
    response = (
        supabase
        .table("equipamentos")
        .update(
            {
                "codigo": codigo,
                "descricao": descricao,
                "classif": classif
            }
        )
        .eq("id", equipamento_id)
        .execute()
    )

    return response.data

def excluir_equipamento(equipamento_id):
    response = (
        supabase
        .table("equipamentos")
        .delete()
        .eq("id", equipamento_id)
        .execute()
    )

    return response.data

def verificar_uso_equipamento(equipamento_id):
    try:

        response = (
            supabase
            .table("produtos")
            .select("id")
            .eq("equipamento_id", equipamento_id)
            .limit(1)
            .execute()
        )

        return len(response.data) > 0

    except Exception:
        return False
        