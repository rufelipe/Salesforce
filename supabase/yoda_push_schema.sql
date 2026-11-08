-- Execute este SQL no SQL Editor do projeto Supabase.
create table if not exists public.push_subscriptions (
  endpoint text primary key,
  subscription jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists public.yoda_reminders (
  task_id text primary key,
  title text not null,
  contract text not null default '',
  starts_at timestamptz not null,
  remind_at timestamptz not null,
  open_url text not null default '/',
  sent_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists yoda_reminders_pending_idx
  on public.yoda_reminders (remind_at) where sent_at is null;

alter table public.push_subscriptions enable row level security;
alter table public.yoda_reminders enable row level security;
-- As tabelas são acessadas somente pelas funções server-side usando service_role.
-- Não exponha SUPABASE_SERVICE_ROLE_KEY no navegador.
