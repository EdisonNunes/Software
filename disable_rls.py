"""
Script para desabilitar RLS na tabela clientes via SQL direto
"""

from config.settings import settings
from supabase import create_client
import os

try:
    config = settings.get_supabase_config()
    
    # Usar PostgREST para executar SQL (se suportado)
    import requests
    import json
    
    url = config["url"]
    key = config["key"]
    
    # Tentar via SQL via endpoint de query (não padrão, pode não funcionar)
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    print("Tentando desabilitar RLS na tabela 'clientes'...")
    print("(Note: Isso requer key de admin/service_role, não anon key)")
    print("\nComo executar manualmente:")
    print("1. Acesse: https://app.supabase.com/project/YOUR_PROJECT/sql/new")
    print("2. Cole este comando:")
    print("\n   ALTER TABLE clientes DISABLE ROW LEVEL SECURITY;")
    print("\n3. Clique em 'Run'")
    
    client = create_client(url, key)
    
    # Testar se agora conseguimos ler dados
    print("\nTestando leitura após comando esperado...")
    response = client.table("clientes").select("*").limit(1).execute()
    print(f"✓ Resposta: {len(response.data)} registros")
    
except Exception as e:
    print(f"Erro: {e}")
