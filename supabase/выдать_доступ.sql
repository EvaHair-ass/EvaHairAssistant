-- Как вручную включить подписку покупательнице (например, после оплаты переводом).
-- Supabase → SQL Editor → вставить, заменить почту и срок → Run.

-- Подписка на 1 месяц от сегодняшнего дня:
update public.subscriptions
set status = 'active', valid_until = now() + interval '1 month', plan = 'month'
where user_id = (select id from auth.users where email = 'почта.покупательницы@example.com');

-- Продлить, если подписка ещё действует (прибавить месяц к текущему сроку):
-- update public.subscriptions
-- set status = 'active', valid_until = greatest(valid_until, now()) + interval '1 month'
-- where user_id = (select id from auth.users where email = 'почта.покупательницы@example.com');

-- Закрыть доступ:
-- update public.subscriptions set status = 'blocked' where user_id = (select id from auth.users where email = 'почта@example.com');

-- Посмотреть всех и сроки:
-- select u.email, s.status, s.plan, s.valid_until from public.subscriptions s join auth.users u on u.id = s.user_id order by s.valid_until;
