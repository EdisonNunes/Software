from supabase import create_client, Client

# Configurações de acesso do Supabase
supabase_url= "https://nrskxiwpinpbjfzzzkht.supabase.co"
supabase_key = "sb_publishable_TLMaVXoyHyrEoCl1YO27IQ_I5zeFeGc"
# Inicializa o cliente do Supabase
supabase: Client = create_client(supabase_url, supabase_key)

def testar_resposta():
    try:
        # Executa a consulta no banco de dados
        response = supabase.table("clientes").select("*").limit(1).execute()
        
        # 2. Testar se a resposta está vazia ou retornou dados corretamente
        # O atributo .data já retorna uma lista com os registros
        if not response.data:
            print("A resposta está vazia (0 registros encontrados).")
        else:
            print("Dados recebidos com sucesso:", response.data)
            
    # 1. Testar se houve erro de rede, RLS ou sintaxe
    # Em Python, os erros do Supabase disparam exceções (PostgrestAPIError)
    except Exception as error:
        print("Erro na API:", getattr(error, "message", str(error)))
        print("Código do erro:", getattr(error, "code", "Desconhecido"))

# Executa a função
testar_resposta()

