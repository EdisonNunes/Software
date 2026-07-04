-- Auditoria completa de schema para alinhamento App x Banco
-- Execute no Supabase SQL Editor com permissao de leitura no catalog.

-- =====================================================
-- 1) Tabelas e colunas (schema public)
-- =====================================================
SELECT
  c.table_schema,
  c.table_name,
  c.column_name,
  c.data_type,
  c.udt_name,
  c.is_nullable,
  c.column_default,
  c.ordinal_position
FROM information_schema.columns c
WHERE c.table_schema = 'public'
ORDER BY c.table_name, c.ordinal_position;

-- =====================================================
-- 2) Views e definicoes
-- =====================================================
SELECT
  v.schemaname AS view_schema,
  v.viewname AS view_name,
  pg_get_viewdef(format('%I.%I', v.schemaname, v.viewname)::regclass, true) AS view_definition
FROM pg_views v
WHERE v.schemaname = 'public'
ORDER BY v.viewname;

-- =====================================================
-- 3) Funcoes (schema public)
-- =====================================================
SELECT
  n.nspname AS function_schema,
  p.proname AS function_name,
  pg_get_function_identity_arguments(p.oid) AS args,
  pg_get_function_result(p.oid) AS returns,
  CASE p.prokind
    WHEN 'f' THEN 'function'
    WHEN 'p' THEN 'procedure'
    WHEN 'a' THEN 'aggregate'
    WHEN 'w' THEN 'window'
    ELSE p.prokind::text
  END AS kind,
  l.lanname AS language
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
JOIN pg_language l ON l.oid = p.prolang
WHERE n.nspname = 'public'
ORDER BY p.proname;

-- =====================================================
-- 4) Triggers
-- =====================================================
SELECT
  n.nspname AS table_schema,
  c.relname AS table_name,
  t.tgname AS trigger_name,
  pg_get_triggerdef(t.oid, true) AS trigger_definition,
  p.proname AS trigger_function
FROM pg_trigger t
JOIN pg_class c ON c.oid = t.tgrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_proc p ON p.oid = t.tgfoid
WHERE NOT t.tgisinternal
  AND n.nspname IN ('public', 'auth')
ORDER BY n.nspname, c.relname, t.tgname;

-- =====================================================
-- 5) Policies (RLS)
-- =====================================================
SELECT
  p.schemaname,
  p.tablename,
  p.policyname,
  p.permissive,
  p.roles,
  p.cmd,
  p.qual,
  p.with_check
FROM pg_policies p
WHERE p.schemaname IN ('public', 'auth')
ORDER BY p.schemaname, p.tablename, p.policyname;

-- =====================================================
-- 6) Tabelas com RLS habilitado
-- =====================================================
SELECT
  n.nspname AS table_schema,
  c.relname AS table_name,
  c.relrowsecurity AS rls_enabled,
  c.relforcerowsecurity AS rls_forced
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
  AND n.nspname IN ('public', 'auth')
ORDER BY n.nspname, c.relname;

-- =====================================================
-- 7) Objetos esperados pelo app (presenca)
-- =====================================================
WITH esperados AS (
  SELECT unnest(ARRAY[
    'clientes','produtos','areas','equipamentos','linhas','metas',
    'processos','paradas','turnos','perfis','servicos','itens_proposta'
  ]) AS obj
)
SELECT
  e.obj AS objeto_esperado,
  CASE WHEN t.table_name IS NOT NULL THEN 'SIM' ELSE 'NAO' END AS tabela_public_existe
FROM esperados e
LEFT JOIN information_schema.tables t
  ON t.table_schema = 'public'
 AND t.table_name = e.obj
ORDER BY e.obj;

-- =====================================================
-- 8) Colunas criticas esperadas no app
-- =====================================================
WITH esperadas AS (
  SELECT * FROM (VALUES
    ('produtos','familia'),
    ('produtos','area_produtiva'),
    ('produtos','area_embalagem'),
    ('produtos','area_rota'),
    ('produtos','equipamento'),
    ('produtos','tempo_ciclo'),
    ('produtos','familia_id'),
    ('produtos','equipamento_id'),
    ('produtos','tempo_ciclo_padrao'),
    ('equipamentos','capacidade'),
    ('equipamentos','unidade_capac'),
    ('equipamentos','unidade_tempo'),
    ('equipamentos','capacidade_nominal'),
    ('equipamentos','unidade_capacidade_id'),
    ('equipamentos','unidade_tempo_id'),
    ('turnos','tipo_turno'),
    ('turnos','vigencia_inicio'),
    ('turnos','vigencia_fim'),
    ('turnos','intervalo_minutos')
  ) AS x(table_name, column_name)
)
SELECT
  e.table_name,
  e.column_name,
  CASE WHEN c.column_name IS NOT NULL THEN 'SIM' ELSE 'NAO' END AS existe_no_banco
FROM esperadas e
LEFT JOIN information_schema.columns c
  ON c.table_schema = 'public'
 AND c.table_name = e.table_name
 AND c.column_name = e.column_name
ORDER BY e.table_name, e.column_name;
