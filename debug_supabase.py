"""
Script para debugar conectividade e dados do Supabase
"""

from config.settings import settings
from supabase import create_client
import json

try:
    # 1. Conectar ao Supabase
    config = settings.get_supabase_config()
   # print(f"✓ Config obtida: URL={config['url'][:50]}...")
    
    client = create_client(config["url"], config["key"])
   # print("✓ Cliente Supabase criado")
    
    # 2. Tentar listar clientes
   # print("\n--- Testando SELECT na tabela 'clientes' ---")
    try:
        response = client.table("clientes").select("*").execute()
      #  print(f"✓ Query executada com sucesso")
      #  print(f"  Status: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
      #  print(f"  Dados retornados: {len(response.data) if response.data else 0} registros")
        
        if response.data:
           # print(f"  Primeiros registros:")
            for item in response.data[:2]:
                print(f"    {item}")
        else:
           print("  ⚠ Nenhum registro retornado!")
            
    except Exception as e:
       print(f"✗ Erro ao ler clientes: {e}")
       print(f"  Tipo: {type(e).__name__}")
    
    # 3. Verificar autenticação/sessão
    print("\n--- Verificando autenticação ---")
    try:
        if hasattr(client.auth, 'get_session'):
            session = client.auth.get_session()
            print(f"✓ Sessão: {session}")
        else:
            print("  Método get_session() não disponível")
    except Exception as e:
        print(f"  Erro ao verificar sessão: {e}")
    
    # 4. Tentar descobrir as tabelas disponíveis
    print("\n--- Verificando tabelas disponíveis ---")
    try:
        # Conectar como admin para verificar RLS
        response = client.table("information_schema").schema("public").execute()
        print(f"  Info schema result: {response}")
    except Exception as e:
        print(f"  Não foi possível consultar information_schema: {e}")
    
    # 5. Testar com count()
    print("\n--- Testando COUNT() ---")
    try:
        response = client.table("clientes").select("count").execute()
        print(f"✓ Count result: {response}")
    except Exception as e:
        print(f"✗ Erro ao fazer count: {e}")
        
except Exception as e:
    print(f"✗ Erro geral: {e}")
    print(f"  Tipo: {type(e).__name__}")
