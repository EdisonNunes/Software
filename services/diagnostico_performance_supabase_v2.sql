-- Pacote de diagnostico de performance (Supabase/Postgres) - V2
-- Foco: tabelas produtos e equipamentos
-- Cliente fixo para as consultas do plano: b36d4cae-9afe-40c6-be8c-3a1df020d91c
-- Esta versao adiciona snapshot historico em tabelas de diagnostico.

-- =====================================================
-- 0) Parametros da execucao
-- =====================================================
WITH params AS (
  SELECT
    'b36d4cae-9afe-40c6-be8c-3a1df020d91c'::uuid AS cliente_id,
    'a'::text AS termo,
    now() AS run_at
)
SELECT * FROM params;

-- =====================================================
-- 1) Estruturas de snapshot (executar uma vez)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.diag_perf_runs (
  id bigserial PRIMARY KEY,
  run_at timestamptz NOT NULL DEFAULT now(),
  cliente_id uuid NOT NULL,
  termo text NOT NULL DEFAULT 'a',
  observacao text NULL
);

CREATE TABLE IF NOT EXISTS public.diag_perf_table_metrics (
  id bigserial PRIMARY KEY,
  run_id bigint NOT NULL REFERENCES public.diag_perf_runs(id) ON DELETE CASCADE,
  tabela text NOT NULL,
  linhas_estimadas bigint,
  linhas_reais bigint,
  linhas_mortas bigint,
  seq_scan bigint,
  idx_scan bigint,
  pct_seq_scan numeric(10,2),
  pct_dead numeric(10,2),
  tamanho_tabela_bytes bigint,
  tamanho_indices_bytes bigint,
  tamanho_total_bytes bigint,
  last_autovacuum timestamptz,
  last_autoanalyze timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.diag_perf_query_metrics (
  id bigserial PRIMARY KEY,
  run_id bigint NOT NULL REFERENCES public.diag_perf_runs(id) ON DELETE CASCADE,
  calls bigint,
  total_ms numeric(18,2),
  media_ms numeric(18,2),
  max_ms numeric(18,2),
  rows_out bigint,
  query_curta text,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- =====================================================
-- 2) Snapshot atual em tabelas historicas
-- =====================================================
WITH params AS (
  SELECT
    'b36d4cae-9afe-40c6-be8c-3a1df020d91c'::uuid AS cliente_id,
    'a'::text AS termo,
    now() AS run_at
),
new_run AS (
  INSERT INTO public.diag_perf_runs (run_at, cliente_id, termo, observacao)
  SELECT run_at, cliente_id, termo, 'Snapshot automatico V2'
  FROM params
  RETURNING id
),
base_tables AS (
  SELECT
    st.relname AS tabela,
    st.n_live_tup AS linhas_estimadas,
    st.n_dead_tup AS linhas_mortas,
    st.seq_scan,
    st.idx_scan,
    CASE
      WHEN (st.seq_scan + st.idx_scan) = 0 THEN 0
      ELSE ROUND((st.seq_scan::numeric / (st.seq_scan + st.idx_scan)::numeric) * 100, 2)
    END AS pct_seq_scan,
    CASE
      WHEN st.n_live_tup = 0 THEN 0
      ELSE ROUND((st.n_dead_tup::numeric / st.n_live_tup::numeric) * 100, 2)
    END AS pct_dead,
    st.last_autovacuum,
    st.last_autoanalyze,
    pg_relation_size(c.oid) AS tamanho_tabela_bytes,
    pg_indexes_size(c.oid) AS tamanho_indices_bytes,
    pg_total_relation_size(c.oid) AS tamanho_total_bytes
  FROM pg_stat_user_tables st
  JOIN pg_class c ON c.relname = st.relname
  JOIN pg_namespace n ON n.oid = c.relnamespace
  WHERE st.schemaname = 'public'
    AND n.nspname = 'public'
    AND st.relname IN ('produtos', 'equipamentos', 'linhas', 'processos')
),
row_counts AS (
  SELECT 'produtos'::text AS tabela, COUNT(*)::bigint AS linhas_reais FROM public.produtos
  UNION ALL
  SELECT 'equipamentos'::text AS tabela, COUNT(*)::bigint AS linhas_reais FROM public.equipamentos
  UNION ALL
  SELECT 'linhas'::text AS tabela, COUNT(*)::bigint AS linhas_reais FROM public.linhas
  UNION ALL
  SELECT 'processos'::text AS tabela, COUNT(*)::bigint AS linhas_reais FROM public.processos
)
INSERT INTO public.diag_perf_table_metrics (
  run_id,
  tabela,
  linhas_estimadas,
  linhas_reais,
  linhas_mortas,
  seq_scan,
  idx_scan,
  pct_seq_scan,
  pct_dead,
  tamanho_tabela_bytes,
  tamanho_indices_bytes,
  tamanho_total_bytes,
  last_autovacuum,
  last_autoanalyze
)
SELECT
  nr.id,
  bt.tabela,
  bt.linhas_estimadas,
  rc.linhas_reais,
  bt.linhas_mortas,
  bt.seq_scan,
  bt.idx_scan,
  bt.pct_seq_scan,
  bt.pct_dead,
  bt.tamanho_tabela_bytes,
  bt.tamanho_indices_bytes,
  bt.tamanho_total_bytes,
  bt.last_autovacuum,
  bt.last_autoanalyze
FROM new_run nr
CROSS JOIN base_tables bt
JOIN row_counts rc ON rc.tabela = bt.tabela;

-- Snapshot de pg_stat_statements (se extensao estiver ativa)
DO $$
DECLARE
  v_run_id bigint;
BEGIN
  SELECT id
  INTO v_run_id
  FROM public.diag_perf_runs
  ORDER BY id DESC
  LIMIT 1;

  IF EXISTS (
    SELECT 1
    FROM pg_extension
    WHERE extname = 'pg_stat_statements'
  ) THEN
    INSERT INTO public.diag_perf_query_metrics (
      run_id,
      calls,
      total_ms,
      media_ms,
      max_ms,
      rows_out,
      query_curta
    )
    SELECT
      v_run_id,
      calls,
      ROUND(total_exec_time::numeric, 2),
      ROUND(mean_exec_time::numeric, 2),
      ROUND(max_exec_time::numeric, 2),
      rows,
      LEFT(query, 250)
    FROM pg_stat_statements
    WHERE query ILIKE '%produtos%'
       OR query ILIKE '%equipamentos%'
       OR query ILIKE '%linhas%'
       OR query ILIKE '%processos%'
    ORDER BY total_exec_time DESC
    LIMIT 30;
  ELSE
    RAISE NOTICE 'Extensao pg_stat_statements nao encontrada. Snapshot de queries nao foi gravado.';
  END IF;
END
$$;

-- =====================================================
-- 3) Consultas de leitura imediata (visao atual)
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
-- 4) EXPLAIN ANALYZE com cliente fixo
-- =====================================================
-- 4.1 Listagem de equipamentos por cliente com ordenacao
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

-- 4.2 Busca textual de equipamentos
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

-- 4.3 Listagem de produtos por cliente com ordenacao
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

-- 4.4 Busca textual de produtos
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
-- 5) Historico recente gravado (comparacao rapida)
-- =====================================================
SELECT
  r.id AS run_id,
  r.run_at,
  r.cliente_id,
  m.tabela,
  m.linhas_reais,
  m.pct_seq_scan,
  pg_size_pretty(m.tamanho_total_bytes) AS tamanho_total,
  m.pct_dead
FROM public.diag_perf_runs r
JOIN public.diag_perf_table_metrics m ON m.run_id = r.id
WHERE r.cliente_id = 'b36d4cae-9afe-40c6-be8c-3a1df020d91c'::uuid
ORDER BY r.id DESC, m.tabela;

-- =====================================================
-- 6) Recomendacoes de indices (quando necessario)
-- =====================================================
-- CREATE INDEX IF NOT EXISTS idx_produtos_cliente_descricao
--   ON public.produtos (cliente_id, descricao);
--
-- CREATE INDEX IF NOT EXISTS idx_equipamentos_cliente_descricao
--   ON public.equipamentos (cliente_id, descricao);
--
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX IF NOT EXISTS idx_produtos_descricao_trgm
--   ON public.produtos USING gin (descricao gin_trgm_ops);
-- CREATE INDEX IF NOT EXISTS idx_equipamentos_descricao_trgm
--   ON public.equipamentos USING gin (descricao gin_trgm_ops);
