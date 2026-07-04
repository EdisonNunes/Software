# Relatorio de compatibilidade App x Banco (2026-07-03)

## Origem do diagnostico
- Leitura de uso de tabelas/colunas no codigo Python.
- Consulta ao OpenAPI do PostgREST com service_role para objetos expostos.
- Validacao por select em tabelas principais com service_role.

## Objetos usados pelo app
- clientes
- produtos
- areas
- equipamentos
- linhas
- metas
- processos
- paradas
- turnos
- perfis
- servicos
- itens_proposta

## Objetos expostos no banco (PostgREST)
### Tabelas principais expostas
- clientes, produtos, areas, equipamentos, linhas, metas, processos, paradas, turnos, perfis

### Nao expostos / inexistentes no schema API
- servicos
- itens_proposta

### Views expostas
- v_clientes_produtos
- vw_gargalos_producao
- vw_oee_equipamento
- vw_oee_ordem
- vw_oee_turno
- vw_turnos

### Funcoes RPC expostas
- current_cliente_id
- current_perfil_role
- fn_agendar_ordens_otimizadas
- fn_agendar_ordens_producao
- fn_calcular_oee_ordem
- fn_capacidade_diaria
- fn_gerar_ordens_producao
- fn_replanejar_ordens_producao
- fn_simular_ordens_producao
- fn_sugerir_ordens_producao
- fn_tempo_producao
- get_cliente_id
- is_admin_or_supervisor

## Incompatibilidades criticas encontradas no codigo

1) Tabela servicos nao existe no schema API atual
- Impacto: quebra em listagem/criacao/edicao/exclusao de servicos.
- Arquivo: services/servicos.py

2) Tabela itens_proposta nao existe no schema API atual
- Impacto: quebra na verificacao de uso de servico.
- Arquivo: services/servicos.py

3) produtos: app usava colunas antigas que nao existem mais
- Colunas antigas usadas no app: familia, area_produtiva, area_embalagem, area_rota, equipamento, tempo_ciclo
- Colunas atuais no banco: familia_id, equipamento_id, tempo_ciclo_padrao, unidade_lote_id, unidade_tempo_id, ean, ativo
- Status: RESOLVIDO (mapeamento aplicado para familia_id, equipamento_id, tempo_ciclo_padrao, unidade_lote_id, unidade_tempo_id, ean)
- Arquivos: pages/crud.py, pages/produtos.py

4) equipamentos: app usava nomes de coluna antigos
- App usa: capacidade, unidade_capac, unidade_tempo
- Banco atual: capacidade_nominal, unidade_capacidade_id, unidade_tempo_id
- Status: RESOLVIDO (mapeamento aplicado para capacidade_nominal, unidade_capacidade_id, unidade_tempo_id)
- Arquivos: pages/crud.py, pages/equipamentos.py

5) turnos: schema atual possui novos campos relevantes
- Banco atual inclui: tipo_turno, vigencia_inicio, vigencia_fim, intervalo_minutos, ordem, permite_hora_extra, codigo
- Status: RESOLVIDO (CRUD e tela tratam tipo_turno, vigencias, intervalo, permite_hora_extra e codigo)
- Arquivos: pages/crud.py, pages/turnos.py

## Incompatibilidades de baixo risco
- perfis possuia cargo_id no banco e app nao considerava esse campo.
- Status: RESOLVIDO (usuarios agora lista/edita cargo_id via tabela cargos)

## Pendencias atuais (apos ajustes)
1) Tabela servicos nao existe no schema API atual
- Impacto: modulo legado de servicos depende de tabelas nao expostas.
- Mitigacao aplicada: services/servicos.py com fallback seguro para leitura e mensagens claras de incompatibilidade.

2) Tabela itens_proposta nao existe no schema API atual
- Impacto: verificacao de uso de servico no legado depende desta tabela.
- Mitigacao aplicada: fallback seguro no servico para nao interromper fluxo geral.

## O que nao foi possivel validar apenas via PostgREST
- Triggers
- Policies RLS completas
- Funcoes nao expostas como RPC

Para isso, executar o arquivo SQL:
- services/auditoria_schema_completa.sql

## Proximos passos recomendados (apos ajustes)
1) Definir destino funcional do modulo de servicos (renomear para tabela nova ou remover do fluxo).
2) Rodar auditoria SQL completa para validar triggers/policies/funcoes internas (services/auditoria_schema_completa.sql).
3) Opcional: criar tabela de dominio explicita para tipos/categorias de parada e tipos de turno, reduzindo dependencia de valores historicos dos dados.
