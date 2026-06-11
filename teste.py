from crud import get_supabase_admin

def alterar_display_name(
    user_id: str,
    nome: str
):
    """
    Altera o Display Name de um usuário no Supabase Auth.

    Args:
        user_id: ID do usuário (auth.users.id)
        nome: Novo nome de exibição

    Returns:
        True se atualizado com sucesso
    """

    admin = get_supabase_admin()

    response = admin.auth.admin.update_user_by_id(
        user_id,
        {
            "user_metadata": {
                "display_name": nome
            }
        }
    )
    print("Resposta da atualização do display name:", response)
    return response

alterar_display_name(
    user_id="6f7d16fd-28a7-435f-8718-ed0f6e52f1d7",nome="Fabio Barreto")
