"""
Benchmark de latencia da camada de aplicacao (Supabase client).
Foco em operacoes de leitura de produtos/equipamentos para baseline e acompanhamento.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from statistics import mean
from typing import Callable, Dict, List, Optional
import tomllib

from supabase import create_client

# Garante que a raiz do projeto esteja no path quando executado via terminal.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from config.settings import settings
except ModuleNotFoundError:
    settings = None


def load_supabase_config() -> Dict[str, Optional[str]]:
    """Carrega config do Supabase via settings, env ou .streamlit/secrets.toml."""
    if settings is not None:
        try:
            cfg = settings.get_supabase_config()
            return {
                "url": cfg.get("url"),
                "key": cfg.get("key"),
                "service_role_key": cfg.get("service_role_key"),
            }
        except Exception:
            pass

    env_url = os.getenv("SUPABASE_URL")
    env_key = os.getenv("SUPABASE_KEY")
    env_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if env_url and env_key:
        return {
            "url": env_url,
            "key": env_key,
            "service_role_key": env_service_role_key,
        }

    secrets_path = PROJECT_ROOT / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        with open(secrets_path, "rb") as f:
            data = tomllib.load(f)
        supa = data.get("supabase", {})
        url = supa.get("SUPABASE_URL")
        key = supa.get("SUPABASE_KEY")
        service_role_key = supa.get("SUPABASE_SERVICE_ROLE_KEY")
        if url and key:
            return {
                "url": url,
                "key": key,
                "service_role_key": service_role_key,
            }

    raise ValueError(
        "Nao foi possivel carregar credenciais Supabase. "
        "Configure SUPABASE_URL/SUPABASE_KEY no ambiente "
        "ou .streamlit/secrets.toml."
    )


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    values_sorted = sorted(values)
    rank = (len(values_sorted) - 1) * p
    low = int(rank)
    high = min(low + 1, len(values_sorted) - 1)
    if low == high:
        return values_sorted[low]
    weight = rank - low
    return values_sorted[low] * (1 - weight) + values_sorted[high] * weight


def run_benchmark(name: str, fn: Callable[[], None], runs: int = 20, warmup: int = 3) -> Dict[str, float]:
    for _ in range(warmup):
        fn()

    timings_ms: List[float] = []
    for _ in range(runs):
        start = time.perf_counter()
        fn()
        end = time.perf_counter()
        timings_ms.append((end - start) * 1000)

    return {
        "runs": runs,
        "avg_ms": round(mean(timings_ms), 2),
        "p50_ms": round(percentile(timings_ms, 0.50), 2),
        "p95_ms": round(percentile(timings_ms, 0.95), 2),
        "max_ms": round(max(timings_ms), 2),
        "min_ms": round(min(timings_ms), 2),
    }


def escolher_cliente(client, cliente_id_arg: Optional[str]) -> Optional[Dict[str, str]]:
    """Seleciona cliente por id informado ou por escolha no terminal."""
    if cliente_id_arg:
        dados = (
            client.table("clientes")
            .select("id, empresa")
            .eq("id", cliente_id_arg)
            .limit(1)
            .execute()
            .data
            or []
        )
        if dados:
            return dados[0]
        print(f"Cliente com id {cliente_id_arg} nao encontrado.")
        return None

    clientes = (
        client.table("clientes")
        .select("id, empresa")
        .order("empresa")
        .limit(100)
        .execute()
        .data
        or []
    )

    if not clientes:
        print(
            "Nenhum cliente retornado pela consulta. "
            "Verifique se existem dados em clientes e se a chave usada permite leitura (RLS)."
        )
        return None

    print("\nClientes encontrados:")
    for i, cli in enumerate(clientes, start=1):
        print(f"{i:>2}. {cli.get('empresa', '(sem nome)')} | {cli.get('id')}")

    if not sys.stdin.isatty():
        print("Ambiente nao interativo: usando o primeiro cliente da lista.")
        return clientes[0]

    while True:
        escolha = input("\nEscolha o numero do cliente (Enter = 1): ").strip()
        if not escolha:
            return clientes[0]
        if escolha.isdigit():
            idx = int(escolha)
            if 1 <= idx <= len(clientes):
                return clientes[idx - 1]
        print("Opcao invalida. Informe um numero da lista.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnostico de latencia de consultas Supabase")
    parser.add_argument(
        "--cliente-id",
        dest="cliente_id",
        help="ID de um cliente especifico para executar o benchmark.",
    )
    args = parser.parse_args()

    cfg = load_supabase_config()
    chave = cfg.get("service_role_key") or cfg.get("key")
    client = create_client(cfg["url"], chave)

    cliente = escolher_cliente(client, args.cliente_id)
    if not cliente:
        return

    cliente_id = cliente["id"]
    empresa = cliente.get("empresa", "(sem nome)")
    termo = "a"

    print("=" * 72)
    print("Benchmark de latencia da aplicacao")
    print(f"Cliente usado: {empresa} ({cliente_id})")
    print("=" * 72)

    bench: Dict[str, Dict[str, float]] = {}

    bench["equip_list_page"] = run_benchmark(
        "equip_list_page",
        lambda: client.table("equipamentos")
        .select("id, codigo, descricao, classif, cliente_id")
        .eq("cliente_id", cliente_id)
        .order("descricao")
        .limit(20)
        .execute(),
    )

    bench["equip_search_ilike"] = run_benchmark(
        "equip_search_ilike",
        lambda: client.table("equipamentos")
        .select("id, codigo, descricao, classif")
        .eq("cliente_id", cliente_id)
        .ilike("descricao", f"%{termo}%")
        .order("descricao")
        .limit(20)
        .execute(),
    )

    bench["prod_list_page"] = run_benchmark(
        "prod_list_page",
        lambda: client.table("produtos")
        .select("id, codigo, descricao, cliente_id")
        .eq("cliente_id", cliente_id)
        .order("descricao")
        .limit(20)
        .execute(),
    )

    bench["prod_search_ilike"] = run_benchmark(
        "prod_search_ilike",
        lambda: client.table("produtos")
        .select("id, codigo, descricao")
        .eq("cliente_id", cliente_id)
        .ilike("descricao", f"%{termo}%")
        .order("descricao")
        .limit(20)
        .execute(),
    )

    for name, metrics in bench.items():
        print(f"\n[{name}]")
        print(f"  runs   : {int(metrics['runs'])}")
        print(f"  avg_ms : {metrics['avg_ms']}")
        print(f"  p50_ms : {metrics['p50_ms']}")
        print(f"  p95_ms : {metrics['p95_ms']}")
        print(f"  max_ms : {metrics['max_ms']}")
        print(f"  min_ms : {metrics['min_ms']}")

    print("\nRecomendacao inicial de meta: p95 < 500ms para listagem e busca.")


if __name__ == "__main__":
    main()
