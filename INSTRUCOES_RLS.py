"""
INSTRUÇÕES PARA DESABILITAR RLS NA TABELA CLIENTES

⚠️  Nota: A chave 'anon' do Supabase não pode desabilitar RLS.
    Você precisa usar a chave 'service_role' ou fazer isso manualmente.

═══════════════════════════════════════════════════════════════════

OPÇÃO A: Via Supabase Dashboard (RECOMENDADO - rápido)
────────────────────────────────────────────────────

1. Acesse https://app.supabase.com
2. Selecione seu projeto
3. Vá para: SQL Editor (no menu esquerdo)
4. Cole este comando:

    ALTER TABLE clientes DISABLE ROW LEVEL SECURITY;

5. Clique no botão "Run" (ou Ctrl+Enter)
6. Teste em http://localhost:8501 para verificar se funciona

═══════════════════════════════════════════════════════════════════

OPÇÃO B: Mais seguro - criar política RLS para usuários autenticados
──────────────────────────────────────────────────────────────────

Se preferir manter RLS ativo, execute no SQL Editor:

    -- Habilitar RLS
    ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
    
    -- Permitir SELECT para qualquer usuário autenticado
    CREATE POLICY "Allow authenticated select"
    ON clientes
    FOR SELECT
    USING (auth.role() = 'authenticated');
    
    -- Permitir INSERT/UPDATE/DELETE para qualquer usuário autenticado
    CREATE POLICY "Allow authenticated write"
    ON clientes
    FOR UPDATE
    USING (auth.role() = 'authenticated');
    
    CREATE POLICY "Allow authenticated insert"
    ON clientes
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');
    
    CREATE POLICY "Allow authenticated delete"
    ON clientes
    FOR DELETE
    USING (auth.role() = 'authenticated');

═══════════════════════════════════════════════════════════════════

DEPOIS DE EXECUTAR:
- Teste novamente no app: http://localhost:8501
- Leia dados usando a página "Cadastro de Clientes"
"""

print(__doc__)

# Teste automático após manual
import time
print("\n⏳ Aguardando execução manual no Supabase...")
print("Quando terminar, pressione Enter aqui para testar:")

try:
    input()
    
    from config.settings import settings
    from supabase import create_client
    
    config = settings.get_supabase_config()
    client = create_client(config["url"], config["key"])
    
    print("\n🔍 Testando conexão...")
    response = client.table("clientes").select("*").limit(5).execute()
    
    if response.data:
        print(f"✅ SUCESSO! Retornando {len(response.data)} registros:")
        for item in response.data:
            print(f"   - {item.get('empresa', 'N/A')} ({item.get('cidade', 'N/A')})")
    else:
        print("❌ Ainda retornando 0 registros. Verifique:")
        print("   1. Se executou o comando SQL corretamente")
        print("   2. Se a tabela realmente tem dados")
        
except KeyboardInterrupt:
    print("\n⏸️  Teste cancelado.")
except Exception as e:
    print(f"❌ Erro: {e}")
