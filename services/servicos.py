"""
Serviço de gerenciamento de serviços.

Fornece operações CRUD para serviços com validação e tratamento de erros.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from core import (
    get_db,
    LoggerManager,
    DatabaseError,
    ValidationError,
    DuplicateServicoError,
    ServicoNotFoundError,
)

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from typing import Any, Dict


def _serializar(valor: Any):
    """
    Converte objetos Python para tipos compatíveis com JSON/Supabase.
    """
    if valor is None:
        return None

    if isinstance(valor, UUID):
        return str(valor)

    if isinstance(valor, (date, datetime)):
        return valor.isoformat()

    if isinstance(valor, Decimal):
        return float(valor)

    if isinstance(valor, dict):
        return {k: _serializar(v) for k, v in valor.items()}

    if isinstance(valor, (list, tuple)):
        return [_serializar(v) for v in valor]

    return valor

logger = LoggerManager.get_logger(__name__)

SCHEMA_INCOMPAT_SERVICOS = (
    "Schema incompatível: tabela 'servicos' não está disponível no banco atual."
)
SCHEMA_INCOMPAT_ITENS = (
    "Schema incompatível: tabela 'itens_proposta' não está disponível no banco atual."
)


def _is_missing_table_error(error: Exception) -> bool:
    msg = str(error)
    return "PGRST205" in msg or "Could not find the table" in msg


@dataclass
class ServicoValidator:
    """Validador de dados de serviço."""
    
    @staticmethod
    def validar_descricao(descricao: str) -> None:
        """Valida campo descricao."""
        if not descricao or not descricao.strip():
            raise ValidationError("Descrição não pode estar vazia")
    
    @staticmethod
    def validar_valor(valor: float) -> None:
        """Valida campo valor."""
        try:
            valor_float = float(valor)
            if valor_float < 0:
                raise ValidationError("Valor não pode ser negativo")
        except (ValueError, TypeError):
            raise ValidationError("Valor deve ser um número válido")
    
    @staticmethod
    def validar_servico(dados: Dict[str, Any]) -> None:
        """Valida todos os campos de serviço."""
        ServicoValidator.validar_descricao(dados.get("descricao", ""))
        ServicoValidator.validar_valor(dados.get("valor", 0))


class ServicoService:
    """Serviço de gerenciamento de serviços."""
    
    def __init__(self):
        """Inicializa serviço com cliente Supabase."""
        self.db = get_db()
        self.validator = ServicoValidator()
        self._table_availability: Dict[str, bool] = {}

    def _is_table_available(self, table_name: str) -> bool:
        """Verifica e cacheia disponibilidade de tabela no PostgREST schema cache."""
        if table_name in self._table_availability:
            return self._table_availability[table_name]

        try:
            self.db.table(table_name).select("*").limit(1).execute()
            self._table_availability[table_name] = True
            return True
        except Exception as e:
            if _is_missing_table_error(e):
                self._table_availability[table_name] = False
                return False
            raise

    def _assert_servicos_schema_available(self) -> None:
        """Garante que as tabelas legadas de serviços estão disponíveis."""
        if not self._is_table_available("servicos"):
            raise DatabaseError(SCHEMA_INCOMPAT_SERVICOS)

    def _assert_itens_proposta_schema_available(self) -> None:
        """Garante disponibilidade da tabela de relacionamento de serviços."""
        if not self._is_table_available("itens_proposta"):
            raise DatabaseError(SCHEMA_INCOMPAT_ITENS)
    
    def listar(self, filtro_descricao: str = "", limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Lista serviços com filtro opcional.
        
        Args:
            filtro_descricao: Filtro por descrição (ilike)
            limit: Número máximo de registros
            
        Returns:
            Lista de serviços
        """
        try:
            self._assert_servicos_schema_available()
            query = self.db.table("servicos").select(
                "id_servico, descricao, valor, ref, codigo, tipo"
            )
            
            if filtro_descricao:
                query = query.filter("descricao", "ilike", f"%{filtro_descricao}%")
            
            query = query.order("descricao", desc=False).limit(limit)
            response = query.execute()
            
            logger.info(f"Listados {len(response.data)} serviços")
            return response.data
        except DatabaseError as e:
            if SCHEMA_INCOMPAT_SERVICOS in str(e):
                logger.warning("Tabela 'servicos' ausente no schema atual; retornando lista vazia")
                return []
            raise
        except Exception as e:
            if _is_missing_table_error(e):
                logger.warning("Tabela 'servicos' ausente no schema atual; retornando lista vazia")
                return []
            logger.error(f"Erro ao listar serviços: {e}")
            raise DatabaseError(f"Erro ao listar serviços: {e}")
    
    def listar_todos(self) -> List[Dict[str, Any]]:
        """
        Lista todos os serviços com todos os campos.
        
        Returns:
            Lista de serviços
        """
        try:
            self._assert_servicos_schema_available()
            response = self.db.table("servicos").select("*").order("descricao", desc=False).execute()
            logger.info(f"Listados {len(response.data)} serviços (todos os campos)")
            return response.data
        except DatabaseError as e:
            if SCHEMA_INCOMPAT_SERVICOS in str(e):
                logger.warning("Tabela 'servicos' ausente no schema atual; retornando lista vazia")
                return []
            raise
        except Exception as e:
            if _is_missing_table_error(e):
                logger.warning("Tabela 'servicos' ausente no schema atual; retornando lista vazia")
                return []
            logger.error(f"Erro ao listar todos os serviços: {e}")
            raise DatabaseError(f"Erro ao listar serviços: {e}")
    
    def obter_por_id(self, id_servico: int) -> Dict[str, Any]:
        """
        Obtém um serviço pelo ID.
        
        Args:
            id_servico: ID do serviço
            
        Returns:
            Dados do serviço
            
        Raises:
            ServicoNotFoundError: Se serviço não existe
        """
        try:
            self._assert_servicos_schema_available()
            response = self.db.table("servicos").select("*").eq("id_servico", id_servico).execute()
            
            if not response.data:
                raise ServicoNotFoundError(f"Serviço {id_servico} não encontrado")
            
            return response.data[0]
            
        except ServicoNotFoundError:
            raise
        except Exception as e:
            if _is_missing_table_error(e):
                raise DatabaseError(SCHEMA_INCOMPAT_SERVICOS)
            logger.error(f"Erro ao obter serviço {id_servico}: {e}")
            raise DatabaseError(f"Erro ao obter serviço: {e}")
    
    def criar(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo serviço.
        
        Args:
            dados: Dados do serviço
            
        Returns:
            Serviço criado
            
        Raises:
            ValidationError: Se dados inválidos
            DuplicateServicoError: Se serviço duplicado
        """
        try:
            self._assert_servicos_schema_available()
            # Validar dados
            self.validator.validar_servico(dados)
            
            # Verificar duplicata
            existe = self.db.table("servicos").select("*") \
                .eq("descricao", dados["descricao"]) \
                .execute()
            
            if existe.data:
                raise DuplicateServicoError(
                    f"Serviço '{dados['descricao']}' já existe"
                )
            
            # Inserir
            response = self.db.table("servicos").insert(dados).execute()
            
            logger.info(f"Serviço criado: {dados['descricao']}")
            return response.data[0] if response.data else {}
            
        except (ValidationError, DuplicateServicoError):
            raise
        except Exception as e:
            if _is_missing_table_error(e):
                raise DatabaseError(SCHEMA_INCOMPAT_SERVICOS)
            logger.error(f"Erro ao criar serviço: {e}")
            raise DatabaseError(f"Erro ao criar serviço: {e}")
    
    def atualizar(self, id_servico: int, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza um serviço existente.
        
        Args:
            id_servico: ID do serviço
            dados: Dados a atualizar
            
        Returns:
            Serviço atualizado
            
        Raises:
            ValidationError: Se dados inválidos
            ServicoNotFoundError: Se serviço não existe
        """
        try:
            self._assert_servicos_schema_available()
            # Validar dados
            self.validator.validar_servico(dados)
            
            # Verificar existência
            self.obter_por_id(id_servico)
            
            # Atualizar
            response = self.db.table("servicos").update(dados).eq("id_servico", id_servico).execute()
            
            logger.info(f"Serviço {id_servico} atualizado")
            return response.data[0] if response.data else {}
            
        except (ValidationError, ServicoNotFoundError):
            raise
        except Exception as e:
            if _is_missing_table_error(e):
                raise DatabaseError(SCHEMA_INCOMPAT_SERVICOS)
            logger.error(f"Erro ao atualizar serviço {id_servico}: {e}")
            raise DatabaseError(f"Erro ao atualizar serviço: {e}")
    
    def excluir(self, id_servico: int) -> None:
        """
        Exclui um serviço.
        
        Args:
            id_servico: ID do serviço
            
        Raises:
            ServicoNotFoundError: Se serviço não existe
        """
        try:
            self._assert_servicos_schema_available()
            # Verificar existência
            self.obter_por_id(id_servico)
            
            # Excluir
            self.db.table("servicos").delete().eq("id_servico", id_servico).execute()
            
            logger.info(f"Serviço {id_servico} excluído")
            
        except ServicoNotFoundError:
            raise
        except Exception as e:
            if _is_missing_table_error(e):
                raise DatabaseError(SCHEMA_INCOMPAT_SERVICOS)
            logger.error(f"Erro ao excluir serviço {id_servico}: {e}")
            raise DatabaseError(f"Erro ao excluir serviço: {e}")
    
    def verificar_uso(self, id_servico: int) -> List[Dict[str, Any]]:
        """
        Verifica se o serviço está em uso em alguma proposta.
        
        Args:
            id_servico: ID do serviço
            
        Returns:
            Lista de propostas que usam o serviço
        """
        try:
            self._assert_servicos_schema_available()
            self._assert_itens_proposta_schema_available()
            response = self.db.table("itens_proposta") \
                .select("propostas(num_proposta, empresa, cidade, data_emissao)") \
                .eq("id_servico", id_servico) \
                .execute()
            
            propostas = []
            if response.data:
                ids_vistos = set()
                for item in response.data:
                    prop = item.get("propostas")
                    if prop:
                        num = prop.get("num_proposta")
                        if num and num not in ids_vistos:
                            ids_vistos.add(num)
                            propostas.append(prop)
            
            logger.info(f"Serviço {id_servico} usado em {len(propostas)} proposta(s)")
            return propostas
        except DatabaseError as e:
            if SCHEMA_INCOMPAT_ITENS in str(e):
                logger.warning(
                    "Tabela de relacionamento de serviços ausente no schema atual; assumindo sem vínculos"
                )
                return []
            raise
        except Exception as e:
            if _is_missing_table_error(e):
                logger.warning(
                    "Tabela de relacionamento de serviços ausente no schema atual; assumindo sem vínculos"
                )
                return []
            logger.error(f"Erro ao verificar uso do serviço {id_servico}: {e}")
            raise DatabaseError(f"Erro ao verificar uso do serviço: {e}")


def _executar_rpc(nome_funcao: str, payload: Dict[str, Any]):
    try:
        db = get_db()
        return db.rpc(nome_funcao, payload).execute()
    except Exception as e:
        logger.error(f"Erro ao executar RPC {nome_funcao}: {e}")
        raise DatabaseError(f"Erro ao executar {nome_funcao}: {e}")
def _executar_rpc(nome_funcao: str, payload: Dict[str, Any]):
    try:
        db = get_db()
        payload_serializado = {
            k: _serializar(v)
            for k, v in payload.items()
        }
        return db.rpc(
            nome_funcao,
            payload_serializado
        ).execute()

    except Exception as e:
        logger.exception(f"Erro ao executar RPC {nome_funcao}")
        raise DatabaseError(
            f"Erro ao executar {nome_funcao}: {e}"
        )

def gerar_ordens(cliente_id, data):
    return _executar_rpc(
        "fn_agendar_ordens_otimizadas",
        {
            "p_cliente_id": cliente_id,
            "p_data": data,
        },
    )


def replanejar(cliente_id, data):
    return _executar_rpc(
        "fn_replanejar_ordens_producao",
        {
            "p_cliente_id": cliente_id,
            "p_data": data,
        },
    )


def simular(cliente_id, data):
    return _executar_rpc(
        "fn_simular_ordens_producao",
        {
            "p_cliente_id": cliente_id,
            "p_data": data,
        },
    )


def oee_ordem(ordem_id):
    return _executar_rpc(
        "fn_calcular_oee_ordem",
        {
            "p_ordem_id": ordem_id,
        },
    )

