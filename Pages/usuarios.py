# create table auth.users (
#   instance_id uuid null,
#   id uuid not null,
#   aud character varying(255) null,
#   role character varying(255) null,
#   email character varying(255) null,
#   encrypted_password character varying(255) null,
#   email_confirmed_at timestamp with time zone null,
#   invited_at timestamp with time zone null,
#   confirmation_token character varying(255) null,
#   confirmation_sent_at timestamp with time zone null,
#   recovery_token character varying(255) null,
#   recovery_sent_at timestamp with time zone null,
#   email_change_token_new character varying(255) null,
#   email_change character varying(255) null,
#   email_change_sent_at timestamp with time zone null,
#   last_sign_in_at timestamp with time zone null,
#   raw_app_meta_data jsonb null,
#   raw_user_meta_data jsonb null,
#   is_super_admin boolean null,
#   created_at timestamp with time zone null,
#   updated_at timestamp with time zone null,
#   phone text null default null::character varying,
#   phone_confirmed_at timestamp with time zone null,
#   phone_change text null default ''::character varying,
#   phone_change_token character varying(255) null default ''::character varying,
#   phone_change_sent_at timestamp with time zone null,
#   confirmed_at timestamp with time zone GENERATED ALWAYS as (LEAST(email_confirmed_at, phone_confirmed_at)) STORED null,
#   email_change_token_current character varying(255) null default ''::character varying,
#   email_change_confirm_status smallint null default 0,
#   banned_until timestamp with time zone null,
#   reauthentication_token character varying(255) null default ''::character varying,
#   reauthentication_sent_at timestamp with time zone null,
#   is_sso_user boolean not null default false,
#   deleted_at timestamp with time zone null,
#   is_anonymous boolean not null default false,
#   constraint users_pkey primary key (id),
#   constraint users_phone_key unique (phone),
#   constraint users_email_change_confirm_status_check check (
#     (
#       (email_change_confirm_status >= 0)
#       and (email_change_confirm_status <= 2)
#     )
#   )
# ) TABLESPACE pg_default;

# create index IF not exists users_instance_id_idx on auth.users using btree (instance_id) TABLESPACE pg_default;

# create index IF not exists users_instance_id_email_idx on auth.users using btree (instance_id, lower((email)::text)) TABLESPACE pg_default;

# create unique INDEX IF not exists confirmation_token_idx on auth.users using btree (confirmation_token) TABLESPACE pg_default
# where
#   ((confirmation_token)::text !~ '^[0-9 ]*$'::text);

# create unique INDEX IF not exists recovery_token_idx on auth.users using btree (recovery_token) TABLESPACE pg_default
# where
#   ((recovery_token)::text !~ '^[0-9 ]*$'::text);

# create unique INDEX IF not exists email_change_token_current_idx on auth.users using btree (email_change_token_current) TABLESPACE pg_default
# where
#   (
#     (email_change_token_current)::text !~ '^[0-9 ]*$'::text
#   );

# create unique INDEX IF not exists email_change_token_new_idx on auth.users using btree (email_change_token_new) TABLESPACE pg_default
# where
#   (
#     (email_change_token_new)::text !~ '^[0-9 ]*$'::text
#   );

# create unique INDEX IF not exists reauthentication_token_idx on auth.users using btree (reauthentication_token) TABLESPACE pg_default
# where
#   (
#     (reauthentication_token)::text !~ '^[0-9 ]*$'::text
#   );

# create unique INDEX IF not exists users_email_partial_key on auth.users using btree (email) TABLESPACE pg_default
# where
#   (is_sso_user = false);

# create index IF not exists users_is_anonymous_idx on auth.users using btree (is_anonymous) TABLESPACE pg_default;

# create index IF not exists idx_users_email on auth.users using btree (email) TABLESPACE pg_default;

# create index IF not exists idx_users_created_at_desc on auth.users using btree (created_at desc) TABLESPACE pg_default;

# create index IF not exists idx_users_last_sign_in_at_desc on auth.users using btree (last_sign_in_at desc) TABLESPACE pg_default;

# create index IF not exists idx_users_name on auth.users using btree (((raw_user_meta_data ->> 'name'::text))) TABLESPACE pg_default
# where
#   ((raw_user_meta_data ->> 'name'::text) is not null);

# create trigger on_auth_user_created_perfis
# after INSERT on auth.users for EACH row
# execute FUNCTION handle_new_auth_user_for_perfis ();
# -------------------------------------------------------------------------------
# Ao executar : incluir_usuario()
# Passo 1 - admin.auth.admin.create_user(...) cria o usuário em auth.users
# Passo 2 - trigger on_auth_user_created_perfis é acionada e chama handle_new_auth_user_for_perfis()
# Passo 3 - handle_new_auth_user_for_perfis() insere o perfil padrão "funcionario" na tabela "perfis" associada ao novo usuário

import streamlit as st
import pandas as pd

from Pages.crud import listar_clientes, listar_usuarios,PERFIS_VALOR, incluir_usuario
from Pages.crud import PERFIS_LABEL, alterar_usuario, excluir_usuario
from components.sidebar import render_app_sidebar
from components.top_menu import render_top_menu
from components.session_state import ensure_session_state

if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

render_app_sidebar()
render_top_menu()

# =====================================================
# SESSION STATE
# =====================================================

ensure_session_state(
    {
        "usuarios_aba": "Listar",
        "usuarios_pagina": 0,
        "usuarios_cliente_pagina": 0,
        "usuarios_cliente_selecionado": None,
        "usuarios_usuario_selecionado": None,
    }
)

PAGE_SIZE = 10

# =====================================================
# SELEÇÃO DA EMPRESA
# =====================================================

if st.session_state.usuarios_cliente_selecionado is None:

    st.subheader("Selecione a Empresa")

    clientes = listar_clientes()

    total = len(clientes)

    inicio = st.session_state.usuarios_cliente_pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE

    st.write(
        f"Mostrando {inicio + 1} - "
        f"{min(fim, total)} "
        f"de {total} registros"
    )

    if clientes:

        clientes_paginados = clientes[inicio:fim]

        df_clientes = pd.DataFrame(
            clientes_paginados
        ).copy()

        df_clientes["Selecionar"] = False

        cols_clientes = [
            "Selecionar",
            "empresa",
            "cidade",
            "telefone",
            "contato"
        ]

        selecao_cli = st.data_editor(
            df_clientes[cols_clientes].reset_index(drop=True),
            hide_index=True,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn(
                    "Selecionar"
                )
            },
            key="usuarios_grid_clientes"
        )

        selecionados = selecao_cli[
            selecao_cli["Selecionar"] == True
        ]

        if len(selecionados) == 1:

            idx = selecionados.index[0]

            if idx < len(clientes_paginados):

                cliente = clientes_paginados[idx]

                st.session_state.usuarios_cliente_selecionado = cliente

                st.rerun()

        elif len(selecionados) > 1:

            st.error(
                "Selecione apenas uma empresa."
            )

    col1, col2, col3 = st.columns([1,2,1])

    total_paginas = max(
        1,
        (total + PAGE_SIZE - 1) // PAGE_SIZE
    )

    if col1.button(
        "⬅️",
        disabled=(
            st.session_state.usuarios_cliente_pagina <= 0
        )
    ):
        st.session_state.usuarios_cliente_pagina -= 1
        st.rerun()

    col2.write(
        f"Página "
        f"{st.session_state.usuarios_cliente_pagina + 1} "
        f"de "
        f"{total_paginas}"
    )

    if col3.button(
        "➡️",
        disabled=(
            st.session_state.usuarios_cliente_pagina + 1
            >= total_paginas
        )
    ):
        st.session_state.usuarios_cliente_pagina += 1
        st.rerun()

    st.stop()

# =====================================================
# EMPRESA SELECIONADA
# =====================================================

cliente = st.session_state.usuarios_cliente_selecionado

st.success(
    f"Empresa Selecionada: "
    f"{cliente['empresa']}"
)

if st.button("Trocar Empresa"):
    st.session_state.usuarios_cliente_selecionado = None
    st.session_state.usuarios_usuario_selecionado = None
    st.rerun()

# =====================================================
# LISTAR
# =====================================================

if st.session_state.usuarios_aba == "Listar":

    usuarios = listar_usuarios(
        cliente["id"]
    )

    total = len(usuarios)

    inicio = st.session_state.usuarios_pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE

    st.write(
        f"Mostrando "
        f"{inicio + 1} - "
        f"{min(fim,total)} "
        f"de {total}"
    )

    if usuarios:

        usuarios_paginados = usuarios[inicio:fim]

        df = pd.DataFrame(
            usuarios_paginados
        ).copy()

        df["Selecionar"] = False

        selecao = st.data_editor(
            df[
                [
                    "Selecionar",
                    "nome",
                    "email",
                    "tipo"
                ]
            ],
            hide_index=True,
            key="usuarios_grid_usuarios"
        )

        selecionados = selecao[
            selecao["Selecionar"] == True
        ]

        if len(selecionados) == 1:

            idx = selecionados.index[0]

            st.session_state.usuarios_usuario_selecionado = (
                usuarios_paginados[idx]
            )

        elif len(selecionados) > 1:

            st.error(
                "Selecione apenas um usuário."
            )

    col1, col2, col3 = st.columns([1,2,1])

    total_paginas = max(
        1,
        (total + PAGE_SIZE - 1) // PAGE_SIZE
    )

    if col1.button(
        "⬅️",
        disabled=st.session_state.usuarios_pagina <= 0
    ):
        st.session_state.usuarios_pagina -= 1
        st.rerun()

    col2.write(
        f"Página "
        f"{st.session_state.usuarios_pagina + 1} "
        f"de "
        f"{total_paginas}"
    )

    if col3.button(
        "➡️",
        disabled=(
            st.session_state.usuarios_pagina + 1
            >= total_paginas
        )
    ):
        st.session_state.usuarios_pagina += 1
        st.rerun()

    col1, col2, col3, col4 = st.columns(4)

    if col1.button("Listar"):
        pass

    if col2.button("Incluir"):
        st.session_state.usuarios_aba = "Incluir"
        st.rerun()

    if col3.button("Alterar"):
        st.session_state.usuarios_aba = "Alterar"
        st.rerun()

    if col4.button("Excluir"):
        st.session_state.usuarios_aba = "Excluir"
        st.rerun()

# =====================================================
# INCLUIR
# =====================================================

elif st.session_state.usuarios_aba == "Incluir":

    st.subheader("Incluir Usuário")

    with st.form("form_incluir_usuario"):

        nome = st.text_input("Nome")

        email = st.text_input("Email")

        senha = st.text_input(
            "Senha",
            type="password"
        )

        # tipo = st.selectbox(
        #     "Tipo",
        #     [
        #         "gerente",
        #         "funcionario"
        #     ]
        # )
        tipo_exibicao = st.selectbox(
            "Tipo",
            [
                "Gerente",
                "Funcionário"
            ]
        )

        tipo = PERFIS_VALOR[tipo_exibicao]

        st.info(
            f"Empresa: "
            f"{cliente['empresa']}"
        )

        col1, col2 = st.columns(2)

        salvar = col1.form_submit_button(
            "Incluir Usuário"
        )

        voltar = col2.form_submit_button(
            "Voltar"
        )

        if salvar:

            incluir_usuario(
                nome,
                email,
                senha,
                tipo,
                cliente["id"]
            )

            st.success(
                "Usuário incluído."
            )

            st.session_state.usuarios_aba = "Listar"

            st.rerun()

        if voltar:

            st.session_state.usuarios_aba = "Listar"

            st.rerun()

# =====================================================
# ALTERAR
# =====================================================

elif st.session_state.usuarios_aba == "Alterar":

    usuario = st.session_state.usuarios_usuario_selecionado

    if usuario is None:

        st.warning(
            "Selecione um usuário."
        )

    else:

        with st.form("form_alterar_usuario"):

            nome = st.text_input(
                "Nome",
                value=usuario["nome"]
            )

            # tipo = st.selectbox(
            #     "Tipo",
            #     [
            #         "gerente",
            #         "funcionario"
            #     ],
            #     index=0 if usuario["tipo"] == "gerente" else 1
            # )
            tipos_exibicao = [
                    "Gerente",
                    "Funcionário"
                ]

            tipo_atual = PERFIS_LABEL.get(
                usuario["tipo"],
                "Gerente"
            )

            tipo_exibicao = st.selectbox(
                "Tipo",
                tipos_exibicao,
                index=tipos_exibicao.index(tipo_atual)
            )

            tipo = PERFIS_VALOR[tipo_exibicao]

            col1, col2 = st.columns(2)

            salvar = col1.form_submit_button(
                "Salvar"
            )

            voltar = col2.form_submit_button(
                "Voltar"
            )

            if salvar:

                alterar_usuario(
                    usuario["id"],
                    nome,
                    tipo
                )

                st.success(
                    "Usuário alterado."
                )

                st.session_state.usuarios_aba = "Listar"

                st.rerun()

            if voltar:

                st.session_state.usuarios_aba = "Listar"

                st.rerun()

# =====================================================
# EXCLUIR
# =====================================================

elif st.session_state.usuarios_aba == "Excluir":

    usuario = st.session_state.usuarios_usuario_selecionado

    if usuario is None:

        st.warning(
            "Selecione um usuário."
        )

    else:

        st.warning(
            f"Deseja excluir "
            f"{usuario['nome']} ?"
        )

        col1, col2 = st.columns(2)

        if col1.button(
            "Excluir Usuário"
        ):

            excluir_usuario(
                usuario["id"]
            )

            st.success(
                "Usuário excluído."
            )

            st.session_state.usuarios_usuario_selecionado = None
            st.session_state.usuarios_aba = "Listar"

            st.rerun()

        if col2.button(
            "Voltar"
        ):

            st.session_state.usuarios_aba = "Listar"

            st.rerun()