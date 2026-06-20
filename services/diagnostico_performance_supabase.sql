-- Pacote de diagnostico de performance (Supabase/Postgres)
-- Foco: tabelas produtos e equipamentos
-- Execute este script no SQL Editor do Supabase.

-- =====================================================
-- 1) Volume atual de dados (estimado e real)
-- =====================================================
SELECT
  relname AS tabela,
  n_live_tup AS linhas_estimadas,
  n_dead_tup AS linhas_mortas,
  last_vacuum,
  last_autovacuum,
  last_analyze,
  last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND relname IN ('produtos', 'equipamentos', 'linhas', 'processos')
ORDER BY relname;

SELECT 'produtos' AS tabela, COUNT(*) AS linhas_reais FROM public.produtos
UNION ALL
SELECT 'equipamentos' AS tabela, COUNT(*) AS linhas_reais FROM public.equipamentos
UNION ALL
SELECT 'linhas' AS tabela, COUNT(*) AS linhas_reais FROM public.linhas
UNION ALL
SELECT 'processos' AS tabela, COUNT(*) AS linhas_reais FROM public.processos;

-- =====================================================
-- 2) Tamanho de tabelas e indices
-- =====================================================
SELECT
  c.relname AS tabela,
  pg_size_pretty(pg_relation_size(c.oid)) AS tamanho_tabela,
  pg_size_pretty(pg_indexes_size(c.oid)) AS tamanho_indices,
  pg_size_pretty(pg_total_relation_size(c.oid)) AS tamanho_total
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relkind = 'r'
  AND c.relname IN ('produtos', 'equipamentos', 'linhas', 'processos')
ORDER BY pg_total_relation_size(c.oid) DESC;

-- =====================================================
-- 3) Inventario de indices e uso
-- =====================================================
SELECT
  t.relname AS tabela,
  i.relname AS indice,
  pg_size_pretty(pg_relation_size(i.oid)) AS tamanho_indice,
  COALESCE(sui.idx_scan, 0) AS idx_scan,
  pg_get_indexdef(i.oid) AS definicao
FROM pg_class t
JOIN pg_namespace n ON n.oid = t.relnamespace
JOIN pg_index x ON t.oid = x.indrelid
JOIN pg_class i ON i.oid = x.indexrelid
LEFT JOIN pg_stat_user_indexes sui ON sui.indexrelid = i.oid
WHERE n.nspname = 'public'
  AND t.relname IN ('produtos', 'equipamentos', 'linhas', 'processos')
ORDER BY t.relname, sui.idx_scan DESC NULLS LAST;

-- =====================================================
-- 4) Sinais de gargalo de leitura (seq scan alto)
-- =====================================================
SELECT
  relname AS tabela,
  seq_scan,
  idx_scan,
  CASE
    WHEN (seq_scan + idx_scan) = 0 THEN 0
    ELSE ROUND((seq_scan::numeric / (seq_scan + idx_scan)::numeric) * 100, 2)
  END AS pct_seq_scan
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND relname IN ('produtos', 'equipamentos', 'linhas', 'processos')
ORDER BY pct_seq_scan DESC, seq_scan DESC;

-- =====================================================
-- 5) Saude de manutencao (vacuum/analyze)
-- =====================================================
SELECT
  relname AS tabela,
  n_live_tup,
  n_dead_tup,
  CASE
    WHEN n_live_tup = 0 THEN 0
    ELSE ROUND((n_dead_tup::numeric / n_live_tup::numeric) * 100, 2)
  END AS pct_dead,
  last_autovacuum,
  last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND relname IN ('produtos', 'equipamentos', 'linhas', 'processos')
ORDER BY pct_dead DESC;

-- =====================================================
-- 6) Top queries mais custosas (pg_stat_statements)
-- =====================================================
-- Se der erro por extensao ausente, rode antes:
-- CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

SELECT
  calls,
  ROUND(total_exec_time::numeric, 2) AS total_ms,
  ROUND(mean_exec_time::numeric, 2) AS media_ms,
  ROUND(max_exec_time::numeric, 2) AS max_ms,
  rows,
  LEFT(query, 250) AS query_curta
FROM pg_stat_statements
WHERE query ILIKE '%produtos%'
   OR query ILIKE '%equipamentos%'
   OR query ILIKE '%linhas%'
   OR query ILIKE '%processos%'
ORDER BY total_exec_time DESC
LIMIT 30;

-- =====================================================
-- 7) Plano de execucao: modelos para EXPLAIN ANALYZE
-- =====================================================
-- Ajuste os valores abaixo antes de executar a secao 7.
-- Dica: pegue um cliente_id real na tabela clientes.

-- 7.1 Listagem de equipamentos por cliente com ordenacao
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
WITH params AS (
  SELECT
    'b36d4cae-9afe-40c6-be8c-3a1df020d91c'::uuid AS cliente_id,
    'a'::text AS termo
)
SELECT id, codigo, descricao, classif, cliente_id
FROM public.equipamentos
WHERE cliente_id = (SELECT cliente_id FROM params)
ORDER BY descricao
LIMIT 20 OFFSET 0;

-- 7.2 Busca textual de equipamentos
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
WITH params AS (
  SELECT
    'b36d4cae-9afe-40c6-be8c-3a1df020d91c'::uuid AS cliente_id,
    'a'::text AS termo
)
SELECT id, codigo, descricao, classif
FROM public.equipamentos
WHERE cliente_id = (SELECT cliente_id FROM params)
  AND descricao ILIKE '%' || (SELECT termo FROM params) || '%'
ORDER BY descricao
LIMIT 20 OFFSET 0;

-- 7.3 Listagem de produtos por cliente com ordenacao
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
WITH params AS (
  SELECT
    'b36d4cae-9afe-40c6-be8c-3a1df020d91c'::uuid AS cliente_id,
    'a'::text AS termo
)
SELECT id, codigo, descricao, cliente_id
FROM public.produtos
WHERE cliente_id = (SELECT cliente_id FROM params)
ORDER BY descricao
LIMIT 20 OFFSET 0;

-- 7.4 Busca textual de produtos
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
WITH params AS (
  SELECT
    'b36d4cae-9afe-40c6-be8c-3a1df020d91c'::uuid AS cliente_id,
    'a'::text AS termo
)
SELECT id, codigo, descricao
FROM public.produtos
WHERE cliente_id = (SELECT cliente_id FROM params)
  AND descricao ILIKE '%' || (SELECT termo FROM params) || '%'
ORDER BY descricao
LIMIT 20 OFFSET 0;

-- =====================================================
-- 8) Check de indices recomendados para o seu padrao atual
-- =====================================================
-- Se ainda nao existir, os mais importantes para listagem por cliente + descricao:
-- CREATE INDEX IF NOT EXISTS idx_produtos_cliente_descricao
--   ON public.produtos (cliente_id, descricao);
--
-- CREATE INDEX IF NOT EXISTS idx_equipamentos_cliente_descricao
--   ON public.equipamentos (cliente_id, descricao);

-- Para busca ILIKE por substring em grande volume, considerar trigram:
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX IF NOT EXISTS idx_produtos_descricao_trgm
--   ON public.produtos USING gin (descricao gin_trgm_ops);
-- CREATE INDEX IF NOT EXISTS idx_equipamentos_descricao_trgm
--   ON public.equipamentos USING gin (descricao gin_trgm_ops);
