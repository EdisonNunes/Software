# Pacote de Diagnostico de Performance

Este pacote foi criado para acompanhar performance antes e depois do crescimento de dados, com foco em produtos e equipamentos.

## Arquivos

- diagnostico_performance_supabase.sql
- diagnostico_performance_supabase_v2.sql
- diagnostico_latencia_app.py

## Versao 2 (cliente fixo)

- Cliente fixo da V2: b36d4cae-9afe-40c6-be8c-3a1df020d91c
- A V2 grava snapshots historicos em:
	- public.diag_perf_runs
	- public.diag_perf_table_metrics
	- public.diag_perf_query_metrics

Use quando quiser comparar evolucao entre execucoes com o mesmo cliente.

## Como executar (Banco)

1. Abra o SQL Editor no Supabase.
2. Copie e execute o arquivo diagnostico_performance_supabase.sql (versao base)
	ou diagnostico_performance_supabase_v2.sql (com historico).
3. Salve os resultados das secoes 1 a 6 para comparacao futura.
4. Na versao base, ajuste os parametros do EXPLAIN ANALYZE conforme necessario.
5. Na V2, o cliente ja vem fixo e pronto para execucao.

## Como executar (Aplicacao)

No terminal do projeto, rode:

python services/diagnostico_latencia_app.py

O script imprime avg, p50, p95, min e max em milissegundos para operacoes de listagem e busca.

## Periodicidade recomendada

- Fase inicial (poucos dados): mensal.
- Apos liberacao para usuarios: semanal nas primeiras 8 semanas.
- Operacao estavel: quinzenal ou ao detectar lentidao.

## O que monitorar com prioridade

1. p95_ms das consultas de busca e listagem de produtos/equipamentos.
2. pct_seq_scan nas tabelas produtos e equipamentos.
3. idx_scan dos indices compostos por cliente_id + descricao.
4. crescimento de tamanho de tabela e indices.
5. n_dead_tup e frequencia de autovacuum/autoanalyze.

## Gatilhos de acao

- p95 acima de 500ms de forma recorrente.
- pct_seq_scan alto em tabelas de grande volume.
- indice critico com idx_scan muito baixo e seq_scan alto.
- crescimento rapido de tamanho sem manutencao adequada.

## Observacoes

- O pacote e diagnostico, nao altera schema automaticamente.
- Se necessario, aplique os indices sugeridos na secao 8 do SQL com cautela e em janela controlada.
