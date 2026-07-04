"""
Módulo CRUD - Compatibilidade com código legado.

Este módulo mantém compatibilidade com o código existente
enquanto direciona para os novos serviços.

DEPRECATED: Use services/clientes.py e services/servicos.py
"""

import logging
import re
from urllib import response
import warnings
import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import date
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
        self._active_token = None

    def _ensure_client(self):
        access_token = st.session_state.get("supabase_access_token")
        refresh_token = st.session_state.get("supabase_refresh_token")

        if self._client is None:
            config = settings.get_supabase_config()
            self._client = create_client(config["url"], config["key"])

        # Atualiza sessão sempre que o token mudar (ex: após logout/novo login)
        if access_token and refresh_token and access_token != self._active_token:
            try:
                self._client.auth.set_session(access_token, refresh_token)
                self._active_token = access_token
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


def _normalizar_texto(valor: Any) -> str:
    return str(valor or "").strip().lower()


def _codigo_sanitizado(texto: str) -> str:
    base = re.sub(r"[^A-Za-z0-9]+", "_", texto or "").strip("_").upper()
    return base[:30] or "FAM"


def _carregar_unidades() -> List[Dict[str, Any]]:
    response = (
        supabase
        .table("unidades")
        .select("id, codigo, descricao, categoria, ativo")
        .order("categoria", desc=False)
        .order("descricao", desc=False)
        .execute()
    )
    return response.data or []


def _resolver_unidade_id(
    unidades: List[Dict[str, Any]],
    valor_entrada: Any,
    codigos_preferidos: Optional[List[str]] = None,
    categoria_preferida: Optional[str] = None,
) -> Optional[str]:
    if not unidades:
        return None

    if isinstance(valor_entrada, str) and "-" in valor_entrada and len(valor_entrada) >= 32:
        return valor_entrada

    texto = _normalizar_texto(valor_entrada)
    if texto:
        for item in unidades:
            if _normalizar_texto(item.get("id")) == texto:
                return item.get("id")
            if _normalizar_texto(item.get("codigo")) == texto:
                return item.get("id")
            if _normalizar_texto(item.get("descricao")) == texto:
                return item.get("id")

        aliases = {
            "litros": "l",
            "unidades": "un",
            "horas": "h",
            "mes": "m",
        }
        codigo_alias = aliases.get(texto)
        if codigo_alias:
            for item in unidades:
                if _normalizar_texto(item.get("codigo")) == codigo_alias:
                    return item.get("id")

    if codigos_preferidos:
        for codigo in codigos_preferidos:
            for item in unidades:
                if _normalizar_texto(item.get("codigo")) == _normalizar_texto(codigo):
                    return item.get("id")

    if categoria_preferida:
        for item in unidades:
            if _normalizar_texto(item.get("categoria")) == _normalizar_texto(categoria_preferida):
                return item.get("id")

    return unidades[0].get("id")


def _resolver_familia_id(cliente_id: str, familia_id: Any, familia_texto: Any) -> Optional[str]:
    if familia_id:
        return familia_id

    if not cliente_id:
        return None

    familias = (
        supabase
        .table("familias_produtos")
        .select("id, codigo, descricao, cliente_id")
        .eq("cliente_id", cliente_id)
        .order("descricao", desc=False)
        .execute()
    ).data or []

    texto = (familia_texto or "").strip()
    if texto:
        texto_norm = _normalizar_texto(texto)
        for item in familias:
            if _normalizar_texto(item.get("descricao")) == texto_norm or _normalizar_texto(item.get("codigo")) == texto_norm:
                return item.get("id")

        novo_codigo = _codigo_sanitizado(texto)
        existente_codigo = {_normalizar_texto(item.get("codigo")) for item in familias}
        if _normalizar_texto(novo_codigo) in existente_codigo:
            novo_codigo = f"{novo_codigo}_{len(familias) + 1}"

        criada = (
            supabase
            .table("familias_produtos")
            .insert(
                {
                    "cliente_id": cliente_id,
                    "codigo": novo_codigo,
                    "descricao": texto,
                    "ativo": True,
                }
            )
            .execute()
        )
        if criada.data:
            return criada.data[0].get("id")

    return familias[0].get("id") if familias else None


def _resolver_equipamento_id(cliente_id: str, equipamento_id: Any, equipamento_texto: Any) -> Optional[str]:
    if equipamento_id:
        return equipamento_id

    if not cliente_id:
        return None

    equipamentos = (
        supabase
        .table("equipamentos")
        .select("id, descricao, codigo, cliente_id")
        .eq("cliente_id", cliente_id)
        .order("descricao", desc=False)
        .execute()
    ).data or []

    texto = _normalizar_texto(equipamento_texto)
    if texto:
        for item in equipamentos:
            if _normalizar_texto(item.get("descricao")) == texto or _normalizar_texto(item.get("codigo")) == texto:
                return item.get("id")

    return equipamentos[0].get("id") if equipamentos else None


def _enriquecer_produtos_legacy(produtos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not produtos:
        return []

    familias = (
        supabase.table("familias_produtos").select("id, descricao, codigo").execute().data
        or []
    )
    equipamentos = (
        supabase.table("equipamentos").select("id, descricao, codigo").execute().data
        or []
    )
    unidades = _carregar_unidades()

    familias_por_id = {item.get("id"): item for item in familias}
    equipamentos_por_id = {item.get("id"): item for item in equipamentos}
    unidades_por_id = {item.get("id"): item for item in unidades}

    saida = []
    for item in produtos:
        registro = dict(item)
        familia = familias_por_id.get(registro.get("familia_id"), {})
        equipamento = equipamentos_por_id.get(registro.get("equipamento_id"), {})
        unidade_lote = unidades_por_id.get(registro.get("unidade_lote_id"), {})
        unidade_tempo = unidades_por_id.get(registro.get("unidade_tempo_id"), {})

        registro["familia"] = familia.get("descricao", "")
        registro["equipamento"] = equipamento.get("descricao", "")
        registro["tempo_ciclo"] = registro.get("tempo_ciclo_padrao")
        registro["unidade_lote"] = unidade_lote.get("codigo") or unidade_lote.get("descricao")
        registro["unidade_tempo"] = unidade_tempo.get("codigo") or unidade_tempo.get("descricao")
        # Campos legados descontinuados no banco, mantidos para nao quebrar telas.
        registro.setdefault("area_produtiva", "")
        registro.setdefault("area_embalagem", "")
        registro.setdefault("area_rota", "")
        saida.append(registro)

    return saida


def _mapear_unidade_para_ui(codigo: str, categoria: str) -> str:
    codigo_norm = _normalizar_texto(codigo)
    categoria_norm = _normalizar_texto(categoria)
    if codigo_norm == "l":
        return "litros"
    if codigo_norm in {"un", "pc"}:
        return "unidades"
    if codigo_norm == "h":
        return "horas"
    if codigo_norm == "m" and categoria_norm == "tempo":
        return "mes"
    return codigo or ""


def _enriquecer_equipamentos_legacy(equipamentos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not equipamentos:
        return []

    unidades = _carregar_unidades()
    unidades_por_id = {item.get("id"): item for item in unidades}
    saida = []

    for item in equipamentos:
        registro = dict(item)
        unidade_capacidade = unidades_por_id.get(registro.get("unidade_capacidade_id"), {})
        unidade_tempo = unidades_por_id.get(registro.get("unidade_tempo_id"), {})
        registro["capacidade"] = registro.get("capacidade_nominal")
        registro["unidade_capac"] = _mapear_unidade_para_ui(
            unidade_capacidade.get("codigo", ""),
            unidade_capacidade.get("categoria", ""),
        )
        registro["unidade_tempo"] = _mapear_unidade_para_ui(
            unidade_tempo.get("codigo", ""),
            unidade_tempo.get("categoria", ""),
        )
        saida.append(registro)

    return saida


def listar_todos_dados_familias_produtos(cliente_id=""):
    query = (
        supabase
        .table("familias_produtos")
        .select("id, codigo, descricao, cliente_id, ativo")
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.eq("ativo", True).order("descricao", desc=False)
    response = query.execute()
    return response.data or []


def listar_unidades(categoria=""):
    query = (
        supabase
        .table("unidades")
        .select("id, codigo, descricao, categoria, ativo")
        .eq("ativo", True)
    )

    if categoria:
        if isinstance(categoria, (list, tuple, set)):
            categorias = [str(item).strip() for item in categoria if str(item).strip()]
            if categorias:
                query = query.in_("categoria", categorias)
        else:
            query = query.eq("categoria", str(categoria).strip())

    query = query.order("categoria", desc=False).order("descricao", desc=False)
    response = query.execute()
    return response.data or []


def listar_familias_produtos(cliente_id="", ativo=None):
    def _filtrar(data):
        filtrado = data or []

        if cliente_id:
            cliente_norm = str(cliente_id)
            por_cliente = []
            for item in filtrado:
                # Schema confirmado: familias_produtos usa cliente_id.
                cli_item = item.get("cliente_id")
                if cli_item is None or str(cli_item) == cliente_norm:
                    por_cliente.append(item)
            filtrado = por_cliente

        if ativo is not None:
            filtrado = [item for item in filtrado if bool(item.get("ativo")) == bool(ativo)]

        return filtrado

    # Busca ampla e aplica filtros em memoria para suportar dados legados.
    query = (
        supabase
        .table("familias_produtos")
        .select("*")
        .order("descricao", desc=False)
    )
    response = query.execute()
    data = _filtrar(response.data or [])

    # Fallback: em alguns ambientes a politica de acesso da tabela pode
    # retornar vazio para o cliente autenticado mesmo havendo dados.
    if not data:
        try:
            admin = get_supabase_admin()
            response_admin = (
                admin
                .table("familias_produtos")
                .select("*")
                .order("descricao", desc=False)
                .execute()
            )
            data_admin = _filtrar(response_admin.data or [])
            if data_admin:
                return data_admin
        except Exception:
            pass

    return data


def incluir_familia_produto(codigo, descricao, cliente_id, ativo=True):
    descricao = (descricao or "").strip()
    if not descricao:
        raise ValueError("Descrição da família é obrigatória.")

    codigo_final = (codigo or "").strip().upper()
    if not codigo_final:
        codigo_final = _codigo_sanitizado(descricao)

    existe = (
        supabase
        .table("familias_produtos")
        .select("id")
        .eq("cliente_id", cliente_id)
        .eq("codigo", codigo_final)
        .limit(1)
        .execute()
    )
    if existe.data:
        raise ValueError("Já existe uma família com esse código para o cliente.")

    response = (
        supabase
        .table("familias_produtos")
        .insert(
            {
                "codigo": codigo_final,
                "descricao": descricao,
                "cliente_id": cliente_id,
                "ativo": bool(ativo),
            }
        )
        .execute()
    )
    return response.data


def alterar_familia_produto(familia_id, codigo, descricao, ativo=None):
    descricao = (descricao or "").strip()
    if not descricao:
        raise ValueError("Descrição da família é obrigatória.")

    codigo_final = (codigo or "").strip().upper()
    if not codigo_final:
        codigo_final = _codigo_sanitizado(descricao)

    atual = (
        supabase
        .table("familias_produtos")
        .select("cliente_id")
        .eq("id", familia_id)
        .limit(1)
        .execute()
    )
    cliente_id = atual.data[0].get("cliente_id") if atual.data else None

    if cliente_id:
        duplicado = (
            supabase
            .table("familias_produtos")
            .select("id")
            .eq("cliente_id", cliente_id)
            .eq("codigo", codigo_final)
            .neq("id", familia_id)
            .limit(1)
            .execute()
        )
        if duplicado.data:
            raise ValueError("Já existe uma família com esse código para o cliente.")

    payload = {
        "codigo": codigo_final,
        "descricao": descricao,
    }
    if ativo is not None:
        payload["ativo"] = bool(ativo)

    response = (
        supabase
        .table("familias_produtos")
        .update(payload)
        .eq("id", familia_id)
        .execute()
    )
    return response.data


def desativar_familia_produto(familia_id):
    response = (
        supabase
        .table("familias_produtos")
        .update({"ativo": False})
        .eq("id", familia_id)
        .execute()
    )
    return response.data


def reativar_familia_produto(familia_id):
    response = (
        supabase
        .table("familias_produtos")
        .update({"ativo": True})
        .eq("id", familia_id)
        .execute()
    )
    return response.data


def listar_todos_dados_unidades(categoria="", ativo=None):
    query = (
        supabase
        .table("unidades")
        .select("id, codigo, descricao, categoria, ativo")
    )

    if categoria:
        if isinstance(categoria, (list, tuple, set)):
            categorias = [str(item).strip() for item in categoria if str(item).strip()]
            if categorias:
                query = query.in_("categoria", categorias)
        else:
            query = query.eq("categoria", str(categoria).strip())

    if ativo is not None:
        query = query.eq("ativo", bool(ativo))

    query = query.order("categoria", desc=False).order("descricao", desc=False)
    response = query.execute()
    return response.data or []


def incluir_unidade(codigo, descricao, categoria, ativo=True):
    descricao = (descricao or "").strip()
    categoria_final = (categoria or "").strip()
    if not descricao:
        raise ValueError("Descrição da unidade é obrigatória.")
    if not categoria_final:
        raise ValueError("Categoria da unidade é obrigatória.")

    codigo_final = (codigo or "").strip().upper()
    if not codigo_final:
        codigo_final = re.sub(r"[^A-Za-z0-9]+", "_", descricao).strip("_").upper()[:30] or "UND"

    existe = (
        supabase
        .table("unidades")
        .select("id")
        .eq("categoria", categoria_final)
        .eq("codigo", codigo_final)
        .limit(1)
        .execute()
    )
    if existe.data:
        raise ValueError("Já existe uma unidade com esse código na categoria informada.")

    response = (
        supabase
        .table("unidades")
        .insert(
            {
                "codigo": codigo_final,
                "descricao": descricao,
                "categoria": categoria_final,
                "ativo": bool(ativo),
            }
        )
        .execute()
    )
    return response.data


def alterar_unidade(unidade_id, codigo, descricao, categoria, ativo=None):
    descricao = (descricao or "").strip()
    categoria_final = (categoria or "").strip()
    if not descricao:
        raise ValueError("Descrição da unidade é obrigatória.")
    if not categoria_final:
        raise ValueError("Categoria da unidade é obrigatória.")

    codigo_final = (codigo or "").strip().upper()
    if not codigo_final:
        codigo_final = re.sub(r"[^A-Za-z0-9]+", "_", descricao).strip("_").upper()[:30] or "UND"

    duplicado = (
        supabase
        .table("unidades")
        .select("id")
        .eq("categoria", categoria_final)
        .eq("codigo", codigo_final)
        .neq("id", unidade_id)
        .limit(1)
        .execute()
    )
    if duplicado.data:
        raise ValueError("Já existe uma unidade com esse código na categoria informada.")

    payload = {
        "codigo": codigo_final,
        "descricao": descricao,
        "categoria": categoria_final,
    }
    if ativo is not None:
        payload["ativo"] = bool(ativo)

    response = (
        supabase
        .table("unidades")
        .update(payload)
        .eq("id", unidade_id)
        .execute()
    )
    return response.data


def desativar_unidade(unidade_id):
    response = (
        supabase
        .table("unidades")
        .update({"ativo": False})
        .eq("id", unidade_id)
        .execute()
    )
    return response.data


def reativar_unidade(unidade_id):
    response = (
        supabase
        .table("unidades")
        .update({"ativo": True})
        .eq("id", unidade_id)
        .execute()
    )
    return response.data


def listar_opcoes_paradas(cliente_id=""):
    query = (
        supabase
        .table("paradas")
        .select("tipo, categoria_oee")
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    response = query.execute()
    data = response.data or []

    tipos_base = ["Planejada", "Não Planejada"]
    categorias_base = ["Disponibilidade", "Performance", "Qualidade"]

    tipos = []
    categorias = []

    for item in data:
        tipo = (item.get("tipo") or "").strip()
        categoria = (item.get("categoria_oee") or "").strip()
        if tipo and tipo not in tipos:
            tipos.append(tipo)
        if categoria and categoria not in categorias:
            categorias.append(categoria)

    for item in tipos_base:
        if item not in tipos:
            tipos.append(item)

    for item in categorias_base:
        if item not in categorias:
            categorias.append(item)

    return {
        "tipos": tipos,
        "categorias_oee": categorias,
    }


def listar_opcoes_classificacao_equipamento(cliente_id=""):
    query = (
        supabase
        .table("equipamentos")
        .select("classif")
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    response = query.execute()
    data = response.data or []

    opcoes = []
    for item in data:
        valor = (item.get("classif") or "").strip()
        if valor and valor not in opcoes:
            opcoes.append(valor)

    for padrao in ["Principal", "Secundário"]:
        if padrao not in opcoes:
            opcoes.append(padrao)

    return opcoes


def listar_cargos(ativo=True):
    query = (
        supabase
        .table("cargos")
        .select("id, descricao, ativo")
        .order("descricao", desc=False)
    )

    if ativo is not None:
        query = query.eq("ativo", bool(ativo))

    response = query.execute()
    return response.data or []


def incluir_cargo(descricao, ativo=True):
    descricao_final = (descricao or "").strip()
    if not descricao_final:
        raise ValueError("Descrição do cargo é obrigatória.")

    existe = (
        supabase
        .table("cargos")
        .select("id")
        .eq("descricao", descricao_final)
        .limit(1)
        .execute()
    )
    if existe.data:
        raise ValueError("Já existe um cargo com essa descrição.")

    response = (
        supabase
        .table("cargos")
        .insert(
            {
                "descricao": descricao_final,
                "ativo": bool(ativo),
            }
        )
        .execute()
    )
    return response.data


def alterar_cargo(cargo_id, descricao, ativo=None):
    descricao_final = (descricao or "").strip()
    if not descricao_final:
        raise ValueError("Descrição do cargo é obrigatória.")

    duplicado = (
        supabase
        .table("cargos")
        .select("id")
        .eq("descricao", descricao_final)
        .neq("id", cargo_id)
        .limit(1)
        .execute()
    )
    if duplicado.data:
        raise ValueError("Já existe um cargo com essa descrição.")

    payload = {"descricao": descricao_final}
    if ativo is not None:
        payload["ativo"] = bool(ativo)

    response = (
        supabase
        .table("cargos")
        .update(payload)
        .eq("id", cargo_id)
        .execute()
    )
    return response.data


def desativar_cargo(cargo_id):
    response = (
        supabase
        .table("cargos")
        .update({"ativo": False})
        .eq("id", cargo_id)
        .execute()
    )
    return response.data


def reativar_cargo(cargo_id):
    response = (
        supabase
        .table("cargos")
        .update({"ativo": True})
        .eq("id", cargo_id)
        .execute()
    )
    return response.data


def listar_opcoes_roles_usuarios():
    response = (
        supabase
        .table("perfis")
        .select("role")
        .execute()
    )

    roles = []
    for item in response.data or []:
        role = (item.get("role") or "").strip().lower()
        if role and role not in roles:
            roles.append(role)

    # O fluxo de cadastro nesta tela deve continuar restrito a gerente/funcionario.
    for role in ["gerente", "funcionario"]:
        if role not in roles:
            roles.append(role)

    return roles
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
    query = supabase.table("clientes").select("id, empresa, cidade, telefone, contato, email, status")
    if filtro_empresa:
        query = query.filter("empresa", "ilike", f"%{filtro_empresa}%")
    query = query.order("empresa", desc=False)
    response = query.execute()
    return response.data

def listar_todos_dados_clientes():
    query = supabase.table("clientes").select("*").order("empresa", desc=False)
    response = query.execute()
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

def desativar_cliente(id):
    supabase.table("clientes").update({"status": False}).eq("id", id).execute()

def reativar_cliente(id):
    supabase.table("clientes").update({"status": True}).eq("id", id).execute()

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
    query = (
        supabase
        .table("produtos")
        .select(
            """
            id,
            codigo,
            descricao,
            cliente_id,
            familia_id,
            equipamento_id,
            lote_padrao,
            tempo_ciclo_padrao,
            unidade_lote_id,
            unidade_tempo_id,
            ean,
            ativo
            """
        )
    )
    
    # Apenas Admin/Supervisor terão acesso a outras empresas,
    # pois a própria RLS permitirá.
    #     
    if filtro_produto:
        query = query.filter("cliente_id", "eq", filtro_produto)
    query = query.order("descricao", desc=False)
    response = query.execute()
    return _enriquecer_produtos_legacy(response.data or [])

def listar_todos_dados_produtos():
    query = (
        supabase
        .table("produtos")
        .select("*")
        .order("descricao", desc=False)
    )
    response = query.execute()
    return _enriquecer_produtos_legacy(response.data or [])

def incluir_produto(dados):
    existe = supabase.table("produtos").select("*") \
        .eq("descricao", dados["descricao"]).execute()
    #   .eq("empresa", dados["empresa"]).eq("cidade", dados["cidade"]).execute()
    if existe.data:
        raise ValueError("Já existe um produto com essa descricao.")

    cliente_id = dados.get("cliente_id")
    if not cliente_id:
        raise ValueError("Cliente obrigatório para incluir produto.")

    unidades = _carregar_unidades()
    familia_id = _resolver_familia_id(cliente_id, dados.get("familia_id"), dados.get("familia"))
    equipamento_id = _resolver_equipamento_id(cliente_id, dados.get("equipamento_id"), dados.get("equipamento"))
    if not familia_id:
        raise ValueError("Não foi possível identificar uma família para o produto.")
    if not equipamento_id:
        raise ValueError("Não foi possível identificar um equipamento para o produto.")
    unidade_lote_id = _resolver_unidade_id(
        unidades,
        dados.get("unidade_lote_id") or dados.get("unidade_lote"),
        codigos_preferidos=["lote", "un", "pc"],
        categoria_preferida="Produção",
    )
    unidade_tempo_id = _resolver_unidade_id(
        unidades,
        dados.get("unidade_tempo_id") or dados.get("unidade_tempo"),
        codigos_preferidos=["min", "h", "s"],
        categoria_preferida="Tempo",
    )

    payload = {
        "codigo": dados.get("codigo"),
        "descricao": dados.get("descricao"),
        "cliente_id": cliente_id,
        "familia_id": familia_id,
        "equipamento_id": equipamento_id,
        "lote_padrao": dados.get("lote_padrao"),
        "tempo_ciclo_padrao": dados.get("tempo_ciclo_padrao", dados.get("tempo_ciclo")),
        "unidade_lote_id": unidade_lote_id,
        "unidade_tempo_id": unidade_tempo_id,
        "ean": dados.get("ean"),
        "ativo": bool(dados.get("ativo", True)),
    }

    supabase.table("produtos").insert(payload).execute()

def alterar_produto(id, dados):
    unidades = _carregar_unidades()

    existing = (
        supabase
        .table("produtos")
        .select("cliente_id")
        .eq("id", id)
        .limit(1)
        .execute()
    )
    cliente_id = (
        dados.get("cliente_id")
        or (existing.data[0].get("cliente_id") if existing.data else None)
    )

    payload = {
        "codigo": dados.get("codigo"),
        "descricao": dados.get("descricao"),
        "lote_padrao": dados.get("lote_padrao"),
        "tempo_ciclo_padrao": dados.get("tempo_ciclo_padrao", dados.get("tempo_ciclo")),
        "ean": dados.get("ean"),
    }

    if cliente_id:
        payload["cliente_id"] = cliente_id
        payload["familia_id"] = _resolver_familia_id(cliente_id, dados.get("familia_id"), dados.get("familia"))
        payload["equipamento_id"] = _resolver_equipamento_id(cliente_id, dados.get("equipamento_id"), dados.get("equipamento"))
        if not payload["familia_id"]:
            raise ValueError("Não foi possível identificar uma família para o produto.")
        if not payload["equipamento_id"]:
            raise ValueError("Não foi possível identificar um equipamento para o produto.")

    unidade_lote_id = _resolver_unidade_id(
        unidades,
        dados.get("unidade_lote_id") or dados.get("unidade_lote"),
        codigos_preferidos=["lote", "un", "pc"],
        categoria_preferida="Produção",
    )
    unidade_tempo_id = _resolver_unidade_id(
        unidades,
        dados.get("unidade_tempo_id") or dados.get("unidade_tempo"),
        codigos_preferidos=["min", "h", "s"],
        categoria_preferida="Tempo",
    )

    if unidade_lote_id:
        payload["unidade_lote_id"] = unidade_lote_id
    if unidade_tempo_id:
        payload["unidade_tempo_id"] = unidade_tempo_id
    if "ativo" in dados:
        payload["ativo"] = bool(dados.get("ativo"))

    supabase.table("produtos").update(payload).eq("id", id).execute()

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

        cargos = listar_cargos(ativo=None)
        cargos_por_id = {item.get("id"): item.get("descricao", "") for item in cargos}

        response = (
            admin
            .table("perfis")
            .select("""
                id,
                role,
                cliente_id,
                cargo_id
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
                    "cargo_id": perfil.get("cargo_id"),
                    "cargo": cargos_por_id.get(perfil.get("cargo_id"), ""),
                    "role": perfil.get("role"),
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
    cliente_id,
    cargo_id=None
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
                "cliente_id": cliente_id,
                "cargo_id": cargo_id,
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
    tipo,
    cargo_id=None
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
                "role": tipo,
                "cargo_id": cargo_id,
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

    return _enriquecer_equipamentos_legacy(response.data or [])

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

    return _enriquecer_equipamentos_legacy(response.data or [])

def incluir_equipamento(*args, **kwargs):
    # Compatibilidade com assinatura antiga e nova.
    if kwargs:
        codigo = kwargs.get("codigo")
        descricao = kwargs.get("descricao")
        classif = kwargs.get("classif")
        linha = kwargs.get("linha")
        processo = kwargs.get("processo")
        capacidade = kwargs.get("capacidade")
        unidade_capac = kwargs.get("unidade_capac")
        unidade_tempo = kwargs.get("unidade_tempo")
        cliente_id = kwargs.get("cliente_id")
    else:
        # Novo formato posicional esperado: 9 argumentos.
        codigo = args[0] if len(args) > 0 else None
        descricao = args[1] if len(args) > 1 else None
        classif = args[2] if len(args) > 2 else None
        linha = args[3] if len(args) > 3 else None
        processo = args[4] if len(args) > 4 else None
        capacidade = args[5] if len(args) > 5 else None
        unidade_capac = args[6] if len(args) > 6 else None
        unidade_tempo = args[7] if len(args) > 7 else None
        cliente_id = args[8] if len(args) > 8 else None

    unidades = _carregar_unidades()
    unidade_capacidade_id = _resolver_unidade_id(
        unidades,
        unidade_capac,
        codigos_preferidos=["kg", "l", "un", "pc"],
        categoria_preferida="Massa",
    )
    unidade_tempo_id = _resolver_unidade_id(
        unidades,
        unidade_tempo,
        codigos_preferidos=["min", "h", "dia"],
        categoria_preferida="Tempo",
    )

    response = (
        supabase
        .table("equipamentos")
        .insert(
            {
                "codigo": codigo,
                "descricao": descricao,
                "classif": classif,
                "linha": linha,
                "processo": processo,
                "capacidade_nominal": capacidade,
                "unidade_capacidade_id": unidade_capacidade_id,
                "unidade_tempo_id": unidade_tempo_id,
                "cliente_id": cliente_id
            }
        )
        .execute()
    )

    return response.data

def alterar_equipamento(
    *args,
    **kwargs
):
    # Compatibilidade com assinatura antiga e nova.
    if kwargs:
        equipamento_id = kwargs.get("equipamento_id") or kwargs.get("id")
        codigo = kwargs.get("codigo")
        classif = kwargs.get("classif")
        descricao = kwargs.get("descricao")
        linha = kwargs.get("linha")
        processo = kwargs.get("processo")
        capacidade = kwargs.get("capacidade")
        unidade_capac = kwargs.get("unidade_capac")
        unidade_tempo = kwargs.get("unidade_tempo")
    else:
        # Formato antigo posicional: (id, codigo, classif, descricao)
        # Formato novo posicional: (id, codigo, classif, descricao, linha, processo, capacidade, unidade_capac, unidade_tempo)
        equipamento_id = args[0] if len(args) > 0 else None
        codigo = args[1] if len(args) > 1 else None
        classif = args[2] if len(args) > 2 else None
        descricao = args[3] if len(args) > 3 else None
        linha = args[4] if len(args) > 4 else None
        processo = args[5] if len(args) > 5 else None
        capacidade = args[6] if len(args) > 6 else None
        unidade_capac = args[7] if len(args) > 7 else None
        unidade_tempo = args[8] if len(args) > 8 else None

    unidades = _carregar_unidades()

    payload = {
        "codigo": codigo,
        "descricao": descricao,
        "classif": classif,
    }

    if linha is not None:
        payload["linha"] = linha
    if processo is not None:
        payload["processo"] = processo
    if capacidade is not None:
        payload["capacidade_nominal"] = capacidade
    if unidade_capac is not None:
        payload["unidade_capacidade_id"] = _resolver_unidade_id(
            unidades,
            unidade_capac,
            codigos_preferidos=["kg", "l", "un", "pc"],
            categoria_preferida="Massa",
        )
    if unidade_tempo is not None:
        payload["unidade_tempo_id"] = _resolver_unidade_id(
            unidades,
            unidade_tempo,
            codigos_preferidos=["min", "h", "dia"],
            categoria_preferida="Tempo",
        )

    response = (
        supabase
        .table("equipamentos")
        .update(payload)
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
        
# ============================================================================================
#  create table public.linhas (
#   id uuid not null default gen_random_uuid (),
#   created_at timestamp with time zone not null default now(),
#   cliente_id uuid not null,
#   codigo text not null,
#   descricao text not null,
#   responsavel text null,
#   constraint linhas_pkey primary key (id),
#   constraint linhas_cliente_id_fkey foreign KEY (cliente_id) references clientes (id) on update CASCADE on delete CASCADE
# ) TABLESPACE pg_default;
# create index IF not exists idx_linhas_cliente_id on public.linhas using btree (cliente_id) TABLESPACE pg_default;
# create index IF not exists idx_linhas_codigo on public.linhas using btree (codigo) TABLESPACE pg_default;
# create index IF not exists idx_linhas_descricao on public.linhas using btree (descricao) TABLESPACE pg_default;

def listar_linhas(cliente_id=""):
    query = (
        supabase
        .table("linhas")
        .select(
            """
            id,
            codigo,
            descricao,
            responsavel,
            cliente_id
            """
        )
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.order("descricao", desc=False)

    response = query.execute()

    return response.data

def listar_todos_dados_linhas(cliente_id=""):
    query = (
        supabase
        .table("linhas")
        .select("*")
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.order("descricao", desc=False)

    response = query.execute()

    return response.data

def incluir_linha(
    codigo,
    descricao,
    responsavel,
    cliente_id
):
    response = (
        supabase
        .table("linhas")
        .insert(
            {
                "codigo": codigo,
                "descricao": descricao,
                "responsavel": responsavel,
                "cliente_id": cliente_id
            }
        )
        .execute()
    )

    return response.data


def alterar_linha(
    linha_id,
    codigo,
    descricao,
    responsavel
):
    response = (
        supabase
        .table("linhas")
        .update(
            {
                "codigo": codigo,
                "descricao": descricao,
                "responsavel": responsavel
            }
        )
        .eq("id", linha_id)
        .execute()
    )

    return response.data

def excluir_linha(linha_id):
    response = (
        supabase
        .table("linhas")
        .delete()
        .eq("id", linha_id)
        .execute()
    )

    return response.data

# def verificar_uso_linha(linha_id):
#     try:

#         response = (
#             supabase
#             .table("produtos")
#             .select("id")
#             .eq("linha_id", linha_id)
#             .limit(1)
#             .execute()
#         )

#         return len(response.data) > 0

#     except Exception:
#         return False

# ============================================================================================
# create table public.metas (
#   id uuid not null default gen_random_uuid (),
#   created_at timestamp with time zone not null default now(),
#   created_by uuid null,
#   updated_at timestamp with time zone null,
#   updated_by uuid null,
#   cliente_id uuid not null,
#   parametro text not null,
#   descricao text null,
#   valor text not null,
#   ativo boolean not null default true,
#   constraint metas_pkey primary key (id),
#   constraint metas_cliente_id_fkey foreign KEY (cliente_id) references clientes (id) on update CASCADE on delete CASCADE
# ) TABLESPACE pg_default;

def listar_metas(cliente_id=""):
    query = (
        supabase
        .table("metas")
        .select(
            """
            id,
            parametro,
            descricao,
            valor,
            ativo,
            cliente_id
            """
        )
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.order("parametro", desc=False)

    response = query.execute()

    return response.data

def listar_todos_dados_metas(cliente_id=""):
    query = (
        supabase
        .table("metas")
        .select("*")
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.order("parametro", desc=False)

    response = query.execute()

    return response.data

def incluir_meta(
    parametro,
    descricao,
    valor,
    cliente_id,
    ativo=True
):
    response = (
        supabase
        .table("metas")
        .insert(
            {
                "parametro": parametro,
                "descricao": descricao,
                "valor": valor,
                "cliente_id": cliente_id,
                "ativo": ativo,
            }
        )
        .execute()
    )

    return response.data

def alterar_meta(
    meta_id,
    valor,
    ativo=None
):
    update_payload = {
        "valor": valor,
    }

    if ativo is not None:
        update_payload["ativo"] = ativo

    response = (
        supabase
        .table("metas")
        .update(update_payload)
        .eq("id", meta_id)
        .execute()
    )

    return response.data

# ============================================================================================
# create table public.processos (
#   id uuid not null default gen_random_uuid (),
#   created_at timestamp with time zone not null default now(),
#   cliente_id uuid not null,
#   codigo text not null,
#   descricao text not null,
#   constraint processos_pkey primary key (id)
# ) TABLESPACE pg_default;

# create index IF not exists processos_cliente_id_idx on public.processos using btree (cliente_id) TABLESPACE pg_default;

# create index IF not exists processos_codigo_idx on public.processos using btree (codigo) TABLESPACE pg_default;

# create index IF not exists processos_descricao_idx on public.processos using btree (descricao) TABLESPACE pg_default;
def listar_procs(cliente_id=""):
    query = (
        supabase
        .table("processos")
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

def listar_todos_dados_procs(cliente_id=""):
    query = (
        supabase
        .table("processos")
        .select("*")
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.order("descricao", desc=False)

    response = query.execute()

    return response.data

def incluir_proc(
    codigo,
    descricao,
    cliente_id
):
    response = (
        supabase
        .table("processos")
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

def alterar_proc(
    area_id,
    codigo,
    descricao
):
    response = (
        supabase
        .table("processos")
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

def excluir_proc(area_id):
    response = (
        supabase
        .table("processos")
        .delete()
        .eq("id", area_id)
        .execute()
    )

    return response.data

# def verificar_uso_proc(area_id):
#     try:

#         response = (
#             supabase
#             .table("produtos")
#             .select("id")
#             .eq("area_id", area_id)
#             .limit(1)
#             .execute()
#         )

#         return len(response.data) > 0

    # except Exception:
    #     return False
# ============================================================================================
# Totais para métricas e dashboards
def contar_clientes():
    response = supabase.table("clientes").select("id", count="exact").execute()
    return response.count or 0

def contar_areas(cliente_id=None):
    query = supabase.table("areas").select("id", count="exact")
    if cliente_id:
        query = query.eq("cliente_id", cliente_id)
    response = query.execute()
    return response.count or 0

def contar_linhas(cliente_id=None):
    query = supabase.table("linhas").select("id", count="exact")
    if cliente_id:
        query = query.eq("cliente_id", cliente_id)
    response = query.execute()
    return response.count or 0
  
def contar_processos(cliente_id=None):
    query = supabase.table("processos").select("id", count="exact")
    if cliente_id:
        query = query.eq("cliente_id", cliente_id)
    response = query.execute()
    return response.count or 0

def contar_equipamentos(cliente_id=None):
    query = supabase.table("equipamentos").select("id", count="exact")
    if cliente_id:
        query = query.eq("cliente_id", cliente_id)
    response = query.execute()
    return response.count or 0

def contar_produtos(cliente_id=None):
    query = supabase.table("produtos").select("id", count="exact")

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)
    response = query.execute()
    return response.count or 0

# ============================================================================================
# create table public.paradas (
#   id uuid not null default gen_random_uuid (),
#   created_at timestamp with time zone not null default now(),
#   cliente_id uuid not null,
#   codigo text not null,
#   descricao text not null,
#   categoria_oee text not null,
#   constraint paradas_pkey primary key (id),
#   constraint paradas_cliente_codigo_unique unique (cliente_id, codigo),
#   constraint paradas_cliente_id_fkey foreign KEY (cliente_id) references clientes (id) on update CASCADE on delete CASCADE,
#   constraint paradas_categoria_oee_check check (
#     (
#       categoria_oee = any (
#         array[
#           'Disponibilidade'::text,
#           'Performance'::text,
#           'Qualidade'::text
#         ]
#       )
#     )
#   ),
#   constraint paradas_codigo_nao_vazio check (
#     (
#       length(
#         TRIM(
#           both
#           from
#             codigo
#         )
#       ) > 0
#     )
#   ),
#   constraint paradas_descricao_nao_vazio check (
#     (
#       length(
#         TRIM(
#           both
#           from
#             descricao
#         )
#       ) > 0
#     )
#   ),
#   constraint paradas_categoria_oee_nao_vazio check (
#     (
#       length(
#         TRIM(
#           both
#           from
#             categoria_oee
#         )
#       ) > 0
#     )
#   )
# ) TABLESPACE pg_default;

# create index IF not exists idx_paradas_cliente_id on public.paradas using btree (cliente_id) TABLESPACE pg_default;
# create index IF not exists idx_paradas_codigo on public.paradas using btree (codigo) TABLESPACE pg_default;
# create index IF not exists idx_paradas_descricao on public.paradas using btree (descricao) TABLESPACE pg_default;
# create index IF not exists idx_paradas_categoria_oee on public.paradas using btree (categoria_oee) TABLESPACE pg_default;
def listar_paradas(cliente_id=""):
    query = (
        supabase
        .table("paradas")
        .select(
            """
            id,
            codigo,
            descricao,
            tipo,
            categoria_oee,
            cliente_id,
            ativo
            """
        )
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.order("descricao", desc=False)

    response = query.execute()
    # print("listar_paradas response:", response.data)  # Debugging line
    return response.data

def listar_todos_dados_paradas(cliente_id=""):
    query = (
        supabase
        .table("paradas")
        .select("*")
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.order("descricao", desc=False)

    response = query.execute()

    return response.data

def incluir_parada(
    codigo,
    descricao,
    tipo,
    categoria_oee,
    cliente_id
):
    response = (
        supabase
        .table("paradas")
        .insert(
            {
                "codigo": codigo,
                "descricao": descricao,
                "tipo": tipo,
                "categoria_oee": categoria_oee,
                "cliente_id": cliente_id
            }
        )
        .execute()
    )

    return response.data


def alterar_parada(
    parada_id,
    codigo,
    descricao,
    tipo,
    categoria_oee,
):
    response = (
        supabase
        .table("paradas")
        .update(
            {
                "codigo": codigo,
                "descricao": descricao,
                "tipo": tipo,
                "categoria_oee": categoria_oee
            }
        )
        .eq("id", parada_id)
        .execute()
    )

    return response.data

def desativar_parada(parada_id):
    response = (
        supabase
        .table("paradas")
        .update({"ativo": False})
        .eq("id", parada_id)
        .execute()
    )

    return response.data


def reativar_parada(parada_id):
    response = (
        supabase
        .table("paradas")
        .update({"ativo": True})
        .eq("id", parada_id)
        .execute()
    )

    return response.data


# ####################################################
# TURNOS  - TABELA TURNOS
# create table public.turnos (
#   id uuid not null default gen_random_uuid (),
#   created_at timestamp with time zone not null default now(),
#   created_by uuid null,
#   updated_at timestamp with time zone null,
#   updated_by uuid null,
#   cliente_id uuid not null,
#   descricao text not null,
#   inicio time without time zone not null,
#   final time without time zone not null,
#   ativo boolean not null default true,
#   constraint turnos_pkey primary key (id),
#   constraint turnos_cliente_descricao_unique unique (cliente_id, descricao),
#   constraint turnos_cliente_id_fkey foreign KEY (cliente_id) references clientes (id) on update CASCADE on delete CASCADE
# ) TABLESPACE pg_default;
# ####################################################
def _turno_ja_existe(cliente_id, descricao, turno_id=None):
    query = (
        supabase
        .table("turnos")
        .select("id")
        .eq("cliente_id", cliente_id)
        .eq("descricao", descricao)
    )

    if turno_id:
        query = query.neq("id", turno_id)

    response = query.execute()
    return bool(response.data)


def listar_opcoes_turnos(cliente_id=""):
    query = (
        supabase
        .table("turnos")
        .select("tipo_turno, intervalo_minutos")
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    response = query.execute()
    data = response.data or []

    tipos = []
    intervalos = []

    for item in data:
        tipo = (item.get("tipo_turno") or "").strip()
        if tipo and tipo not in tipos:
            tipos.append(tipo)

        intervalo = item.get("intervalo_minutos")
        if intervalo is not None:
            try:
                val = int(intervalo)
                if val not in intervalos:
                    intervalos.append(val)
            except (TypeError, ValueError):
                pass

    for padrao in ["Produção", "Administrativo", "Regular"]:
        if padrao not in tipos:
            tipos.append(padrao)

    for padrao in [0, 15, 30, 45, 60]:
        if padrao not in intervalos:
            intervalos.append(padrao)

    intervalos.sort()

    return {
        "tipos": tipos,
        "intervalos": intervalos,
    }


def listar_turnos(cliente_id=""):
    query = (
        supabase
        .table("turnos")
        .select(
            """
            id,
            codigo,
            descricao,
            inicio,
            final,
            cliente_id,
            ativo,
            tipo_turno,
            vigencia_inicio,
            vigencia_fim,
            intervalo_minutos,
            permite_hora_extra,
            ordem
            """
        )
    )

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.order("descricao", desc=False)

    response = query.execute()
    return response.data


def listar_todos_dados_turnos(cliente_id=""):
    query = supabase.table("turnos").select("*")

    if cliente_id:
        query = query.eq("cliente_id", cliente_id)

    query = query.order("descricao", desc=False)

    response = query.execute()
    return response.data


def incluir_turno(descricao, inicio, final, cliente_id, ativo=True):
    descricao = (descricao or "").strip()
    if _turno_ja_existe(cliente_id, descricao):
        raise ValueError("Já existe um turno com essa descrição para este cliente.")

    codigo = re.sub(r"[^A-Za-z0-9]+", "_", descricao).strip("_").upper()[:30] or "TURNO"

    # Suporte retrocompatível: páginas antigas enviam somente 5 parâmetros.
    tipo_turno = "Regular"
    vigencia_inicio = date.today().isoformat()
    vigencia_fim = None
    intervalo_minutos = 0
    permite_hora_extra = False
    ordem = 1

    # Permite payload opcional sem quebrar chamadas existentes.
    if isinstance(ativo, dict):
        payload_extra = ativo
        ativo = bool(payload_extra.get("ativo", True))
        tipo_turno = payload_extra.get("tipo_turno", tipo_turno)
        vigencia_inicio = payload_extra.get("vigencia_inicio", vigencia_inicio)
        vigencia_fim = payload_extra.get("vigencia_fim", vigencia_fim)
        intervalo_minutos = int(payload_extra.get("intervalo_minutos", intervalo_minutos) or 0)
        permite_hora_extra = bool(payload_extra.get("permite_hora_extra", permite_hora_extra))
        ordem = int(payload_extra.get("ordem", ordem) or 1)
        codigo = (payload_extra.get("codigo") or codigo).strip() if payload_extra.get("codigo") else codigo

    response = (
        supabase
        .table("turnos")
        .insert(
            {
                "codigo": codigo,
                "descricao": descricao,
                "inicio": inicio,
                "final": final,
                "cliente_id": cliente_id,
                "ativo": ativo,
                "tipo_turno": tipo_turno,
                "vigencia_inicio": vigencia_inicio,
                "vigencia_fim": vigencia_fim,
                "intervalo_minutos": intervalo_minutos,
                "permite_hora_extra": permite_hora_extra,
                "ordem": ordem,
            }
        )
        .execute()
    )

    return response.data


def alterar_turno(turno_id, descricao, inicio, final, ativo=None):
    descricao = (descricao or "").strip()

    existing = (
        supabase
        .table("turnos")
        .select("cliente_id")
        .eq("id", turno_id)
        .execute()
    )

    cliente_id = existing.data[0]["cliente_id"] if existing.data else None
    if cliente_id and _turno_ja_existe(cliente_id, descricao, turno_id=turno_id):
        raise ValueError("Já existe um turno com essa descrição para este cliente.")

    codigo = re.sub(r"[^A-Za-z0-9]+", "_", descricao).strip("_").upper()[:30] or "TURNO"

    update_payload = {
        "codigo": codigo,
        "descricao": descricao,
        "inicio": inicio,
        "final": final,
    }

    if ativo is not None:
        if isinstance(ativo, dict):
            update_payload["ativo"] = bool(ativo.get("ativo", True))
            if ativo.get("tipo_turno") is not None:
                update_payload["tipo_turno"] = ativo.get("tipo_turno")
            if ativo.get("vigencia_inicio") is not None:
                update_payload["vigencia_inicio"] = ativo.get("vigencia_inicio")
            update_payload["vigencia_fim"] = ativo.get("vigencia_fim")
            if ativo.get("intervalo_minutos") is not None:
                update_payload["intervalo_minutos"] = int(ativo.get("intervalo_minutos") or 0)
            if ativo.get("permite_hora_extra") is not None:
                update_payload["permite_hora_extra"] = bool(ativo.get("permite_hora_extra"))
            if ativo.get("ordem") is not None:
                update_payload["ordem"] = int(ativo.get("ordem") or 1)
            if ativo.get("codigo"):
                update_payload["codigo"] = str(ativo.get("codigo")).strip()
        else:
            update_payload["ativo"] = ativo

    response = (
        supabase
        .table("turnos")
        .update(update_payload)
        .eq("id", turno_id)
        .execute()
    )

    return response.data


def desativar_turno(turno_id):
    response = (
        supabase
        .table("turnos")
        .update({"ativo": False})
        .eq("id", turno_id)
        .execute()
    )

    return response.data


def reativar_turno(turno_id):
    response = (
        supabase
        .table("turnos")
        .update({"ativo": True})
        .eq("id", turno_id)
        .execute()
    )

    return response.data

