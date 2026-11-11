-- «Моя мастерская»: схема базы данных Supabase.
-- Как применить: Supabase → SQL Editor → New query → вставить весь файл → Run.
-- Можно запускать повторно: команды безопасны при повторе.

-- 1. Данные пользовательницы: один JSON-документ на человека (склад, закупки, работы, архив, академия).
create table if not exists public.user_state (
  user_id    uuid primary key references auth.users(id) on delete cascade,
  data       jsonb       not null default '{}'::jsonb,
  rev        integer     not null default 1,          -- номер версии: защита от потери данных при записи с двух устройств
  updated_at timestamptz not null default now()
);

-- 2. Подписки: статус доступа. Менять может только владелец проекта (через панель или SQL), не приложение.
create table if not exists public.subscriptions (
  user_id     uuid primary key references auth.users(id) on delete cascade,
  status      text        not null default 'trial' check (status in ('trial','active','expired','blocked')),
  valid_until timestamptz not null,
  plan        text,
  note        text,
  created_at  timestamptz not null default now()
);

alter table public.user_state    enable row level security;
alter table public.subscriptions enable row level security;

-- 2а. Права ролей (работают при любых настройках проекта): вошедшая пользовательница читает и пишет только через правила ниже, без входа доступа нет.
revoke all on public.user_state, public.subscriptions from anon;
grant select, insert, update on public.user_state to authenticated;
grant select on public.subscriptions to authenticated;

-- 3. Проверка доступа: пробный период или оплаченная подписка и срок не истёк.
create or replace function public.has_access(uid uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from public.subscriptions s
    where s.user_id = uid and s.status in ('trial','active') and s.valid_until > now()
  );
$$;

-- 4. Правила доступа. Читать можно всегда (чтобы забрать свои данные), писать только при активном доступе.
drop policy if exists "state: read own"   on public.user_state;
drop policy if exists "state: insert own" on public.user_state;
drop policy if exists "state: update own" on public.user_state;
create policy "state: read own"   on public.user_state for select using (auth.uid() = user_id);
create policy "state: insert own" on public.user_state for insert with check (auth.uid() = user_id and public.has_access(auth.uid()));
create policy "state: update own" on public.user_state for update using (auth.uid() = user_id and public.has_access(auth.uid()))
                                                               with check (auth.uid() = user_id and public.has_access(auth.uid()));

drop policy if exists "subs: read own" on public.subscriptions;
create policy "subs: read own" on public.subscriptions for select using (auth.uid() = user_id);
-- (на запись в subscriptions правил для приложения нет: подписку выдаёт только владелец проекта)

-- 5. Новая пользовательница получает пробный период. Срок меняется числом дней ниже.
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.subscriptions (user_id, status, valid_until, plan)
  values (new.id, 'trial', now() + interval '14 days', 'trial')
  on conflict (user_id) do nothing;
  return new;
end;
$$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- 6. Хранилище фото: закрытая папка, у каждой пользовательницы своя подпапка.
insert into storage.buckets (id, name, public) values ('photos', 'photos', false) on conflict (id) do nothing;

drop policy if exists "photos: read own"   on storage.objects;
drop policy if exists "photos: insert own" on storage.objects;
create policy "photos: read own" on storage.objects for select
  using (bucket_id = 'photos' and (storage.foldername(name))[1] = auth.uid()::text);
create policy "photos: insert own" on storage.objects for insert
  with check (bucket_id = 'photos' and (storage.foldername(name))[1] = auth.uid()::text and public.has_access(auth.uid()));

-- 7. ВАЖНО для тебя как владельца: сделай свой аккаунт постоянным (после того как зарегистрируешься в приложении).
-- Замени почту и запусти отдельным запросом:
-- update public.subscriptions set status = 'active', valid_until = now() + interval '10 years', plan = 'owner'
-- where user_id = (select id from auth.users where email = 'ТВОЯ_ПОЧТА@example.com');
