-- Zumee operations database · Postgres (Supabase)
-- v1 · September 2026
-- Apply once in the Supabase SQL editor (or: psql "$DATABASE_URL" -f schema.sql).

create extension if not exists pgcrypto;

-- ---------- helpers ----------
create or replace function set_updated_at() returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end $$;

-- ---------- drivers (车主) ----------
create table if not exists drivers (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  status          text not null default 'new'
                  check (status in ('new','reviewing','approved','paused','rejected','left')),
  full_name       text,
  first_name      text,
  phone           text not null,
  email           text,
  neighbourhood   text not null,              -- 居住社区，登记时填写
  city            text default 'Metro Vancouver',
  language        text default 'zh',           -- 通知语言 zh/en
  insurance_confirmed boolean not null default false,
  declined_categories text[] default '{}',     -- 车主拒绝的广告类别
  agreement_version text,                      -- 已接受的车主协议版本
  agreement_accepted_at timestamptz,
  source          text default 'website',
  notes           text
);
create index if not exists drivers_status_idx on drivers(status);
create index if not exists drivers_phone_idx on drivers(phone);
create trigger drivers_updated before update on drivers for each row execute function set_updated_at();

-- ---------- vehicles (车辆) ----------
create table if not exists vehicles (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  driver_id       uuid not null references drivers(id) on delete cascade,
  status          text not null default 'pending'
                  check (status in ('pending','available','booked','inactive','rejected')),
  make            text not null,
  model           text,
  year            int check (year between 1990 and 2035),
  colour          text,
  plate           text,                        -- 仅内部使用，不给商家
  tier            text default 'standard' check (tier in ('standard','premium')),
  monthly_km      int,
  photo_url       text,                        -- 登记照片（R2）
  paint_condition text,                        -- 安装前漆面记录
  notes           text
);
create index if not exists vehicles_driver_idx on vehicles(driver_id);
create index if not exists vehicles_status_idx on vehicles(status);
create trigger vehicles_updated before update on vehicles for each row execute function set_updated_at();

-- ---------- businesses (商家) ----------
create table if not exists businesses (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  status          text not null default 'lead'
                  check (status in ('lead','contacted','quoted','signed','active','paused','churned','lost')),
  legal_name      text,                        -- 合同用法定名称
  trade_name      text,                        -- 店名
  contact_name    text,
  contact_title   text,
  phone           text not null,
  email           text,
  address         text,
  category        text,                        -- 房产经纪 / 餐饮 / 家庭服务 ...
  product         text,                        -- 想推广什么（表单原文）
  language        text default 'zh',
  source          text default 'website',
  stripe_customer_id text,
  notes           text
);
create index if not exists businesses_status_idx on businesses(status);
create trigger businesses_updated before update on businesses for each row execute function set_updated_at();

-- ---------- orders (商家订单 = 附件 A) ----------
create table if not exists orders (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  order_no        text unique,                 -- ZM-ORD-0001，由触发器生成
  business_id     uuid not null references businesses(id),
  status          text not null default 'draft'
                  check (status in ('draft','sent','signed','invoiced','paid','in_production','live','completed','cancelled')),
  vehicles_count  int not null default 1,
  tier            text not null default 'standard' check (tier in ('standard','premium')),
  months          int not null default 3,
  start_from      date,
  start_to        date,
  neighbourhood_pref text,
  artwork_source  text default 'client' check (artwork_source in ('client','zumee')),
  panel_spec      text,
  restricted_category text default 'none',
  monthly_fee_per_vehicle numeric(10,2) not null default 0,
  setup_fee_per_vehicle   numeric(10,2) not null default 0,
  removal_fee             numeric(10,2) not null default 0,
  gst_rate        numeric(5,4) not null default 0.05,
  pst_rate        numeric(5,4) not null default 0,   -- 如会计师确认磁贴部分要收 PST 再填
  special_conditions text,
  -- 电子签约
  sign_token      text unique,
  sign_token_expires_at timestamptz,
  sent_at         timestamptz,
  signed_at       timestamptz,
  signature_id    uuid,                        -- -> signatures.id
  signed_pdf_url  text,
  agreement_version text default 'v1.0',
  notes           text
);
create index if not exists orders_business_idx on orders(business_id);
create index if not exists orders_status_idx on orders(status);
create trigger orders_updated before update on orders for each row execute function set_updated_at();

create sequence if not exists order_no_seq start 1;
create or replace function assign_order_no() returns trigger language plpgsql as $$
begin
  if new.order_no is null then
    new.order_no := 'ZM-ORD-' || lpad(nextval('order_no_seq')::text, 4, '0');
  end if;
  return new;
end $$;
create trigger orders_order_no before insert on orders for each row execute function assign_order_no();

-- ---------- campaigns (一辆车 × 一个订单 = 一次投放) ----------
create table if not exists campaigns (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  order_id        uuid not null references orders(id),
  vehicle_id      uuid references vehicles(id),
  driver_id       uuid references drivers(id),
  status          text not null default 'invited'
                  check (status in ('invited','accepted','declined','expired','scheduled','installed','live','interrupted','removed','settled','cancelled')),
  monthly_pay     numeric(10,2) not null default 0,   -- 付给车主的月报酬
  panel_spec      text,
  placement       text,
  -- 车主接受邀请 + 点击同意协议
  accept_token    text unique,
  accept_token_expires_at timestamptz,
  invited_at      timestamptz,
  responded_at    timestamptz,
  signature_id    uuid,                        -- -> signatures.id
  campaign_pdf_url text,
  -- 安装与投放
  install_date    date,
  display_start   date,                        -- 展示开始日，期限从这天起算
  display_end_planned date,
  removed_at      date,
  interruption_days int not null default 0,
  notes           text
);
create index if not exists campaigns_order_idx on campaigns(order_id);
create index if not exists campaigns_driver_idx on campaigns(driver_id);
create index if not exists campaigns_status_idx on campaigns(status);
create trigger campaigns_updated before update on campaigns for each row execute function set_updated_at();

-- ---------- signatures (电子签约记录，商家和车主共用) ----------
create table if not exists signatures (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  party_type      text not null check (party_type in ('business','driver')),
  entity_type     text not null check (entity_type in ('order','campaign','driver')),
  entity_id       uuid not null,
  document_name   text not null,               -- e.g. Advertising Services Agreement + Schedule A
  document_version text not null,
  document_sha256 text not null,               -- 签署时展示文本的哈希，证明签的是哪个版本
  signer_name     text not null,
  signer_title    text,
  signer_email    text,
  signer_phone    text,
  signature_image_url text,                    -- 手写签名图（商家）
  consent_text    text not null,               -- 勾选的那句话原文
  ip              inet,
  user_agent      text,
  accepted_at     timestamptz not null default now(),
  pdf_url         text                         -- 合成后的签署版 PDF（R2）
);
create index if not exists signatures_entity_idx on signatures(entity_type, entity_id);
alter table orders add constraint orders_signature_fk foreign key (signature_id) references signatures(id);
alter table campaigns add constraint campaigns_signature_fk foreign key (signature_id) references signatures(id);

-- ---------- checkins (打卡：每周照片 / 月初月末里程表) ----------
create table if not exists checkins (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  campaign_id     uuid not null references campaigns(id) on delete cascade,
  type            text not null check (type in ('weekly_photo','odometer_start','odometer_end')),
  period_start    date not null,               -- 所属周的周一，或所属月的 1 号
  photo_url       text,
  odometer_km     int,
  submitted_at    timestamptz,
  ip              inet,
  status          text not null default 'due'
                  check (status in ('due','reminded','submitted','ok','rejected','missed')),
  reviewed_at     timestamptz,
  note            text,
  unique (campaign_id, type, period_start)
);
create index if not exists checkins_campaign_idx on checkins(campaign_id);
create index if not exists checkins_status_idx on checkins(status);

-- ---------- invoices (商家发票，Stripe 同步) ----------
create table if not exists invoices (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  order_id        uuid not null references orders(id),
  invoice_no      text unique,                 -- ZM-2026-0001
  stripe_invoice_id text unique,
  kind            text not null default 'first' check (kind in ('first','monthly','renewal','adjustment')),
  period_start    date,
  period_end      date,
  subtotal        numeric(10,2) not null default 0,
  gst             numeric(10,2) not null default 0,
  pst             numeric(10,2) not null default 0,
  total           numeric(10,2) not null default 0,
  status          text not null default 'draft' check (status in ('draft','sent','paid','overdue','void')),
  issued_at       timestamptz,
  due_at          date,
  paid_at         timestamptz,
  paid_method     text,                        -- e-transfer / card / eft
  pdf_url         text
);
create index if not exists invoices_order_idx on invoices(order_id);
create trigger invoices_updated before update on invoices for each row execute function set_updated_at();

create sequence if not exists invoice_no_seq start 1;
create or replace function assign_invoice_no() returns trigger language plpgsql as $$
begin
  if new.invoice_no is null then
    new.invoice_no := 'ZM-' || to_char(now(),'YYYY') || '-' || lpad(nextval('invoice_no_seq')::text, 4, '0');
  end if;
  return new;
end $$;
create trigger invoices_invoice_no before insert on invoices for each row execute function assign_invoice_no();

-- ---------- payouts (车主月结) ----------
create table if not exists payouts (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  campaign_id     uuid not null references campaigns(id),
  driver_id       uuid not null references drivers(id),
  period_month    date not null,               -- 该月 1 号
  days_total      int not null,
  days_displayed  int not null,
  amount          numeric(10,2) not null,
  status          text not null default 'pending' check (status in ('pending','approved','paid','held')),
  method          text,                        -- e-transfer / stripe
  reference       text,
  paid_at         timestamptz,
  note            text,
  unique (campaign_id, period_month)
);
create trigger payouts_updated before update on payouts for each row execute function set_updated_at();

-- ---------- events (审计日志 + 自动化触发记录) ----------
create table if not exists events (
  id              bigserial primary key,
  created_at      timestamptz not null default now(),
  entity_type     text not null,
  entity_id       uuid,
  type            text not null,               -- e.g. order.sent, order.signed, checkin.reminded, invoice.paid
  actor           text default 'system',
  payload         jsonb default '{}'::jsonb
);
create index if not exists events_entity_idx on events(entity_type, entity_id);

-- ---------- settings ----------
create table if not exists settings (
  key   text primary key,
  value text
);
insert into settings(key,value) values
  ('company_name','1376107 B.C. Ltd. dba Zumee'),
  ('gst_number','707470902 RT0001'),
  ('agreement_version_business','v1.0'),
  ('agreement_version_driver','v1.0'),
  ('checkin_weekday','1'),           -- 每周一提醒拍照
  ('payment_terms_days','7')
on conflict (key) do nothing;

-- ---------- views for the admin UI ----------
create or replace view v_driver_pipeline as
select d.id, d.status, d.full_name, d.phone, d.neighbourhood, d.insurance_confirmed,
       v.make, v.model, v.year, v.tier, v.monthly_km, v.status as vehicle_status, d.created_at
from drivers d left join vehicles v on v.driver_id = d.id;

create or replace view v_order_summary as
select o.id, o.order_no, o.status, b.trade_name, b.contact_name, b.phone,
       o.vehicles_count, o.tier, o.months, o.monthly_fee_per_vehicle,
       (o.monthly_fee_per_vehicle + o.setup_fee_per_vehicle) * o.vehicles_count as first_invoice_subtotal,
       o.sent_at, o.signed_at, o.created_at,
       (select count(*) from campaigns c where c.order_id = o.id and c.status in ('accepted','scheduled','installed','live')) as vehicles_filled
from orders o join businesses b on b.id = o.business_id;

create or replace view v_checkins_due as
select c.id as checkin_id, c.type, c.period_start, c.status, cp.id as campaign_id,
       d.full_name, d.phone, d.email, d.language, o.order_no
from checkins c
join campaigns cp on cp.id = c.campaign_id
join drivers d on d.id = cp.driver_id
join orders o on o.id = cp.order_id
where c.status in ('due','reminded');

-- ---------- security: only the service role (used by the API) may read/write ----------
alter table drivers enable row level security;
alter table vehicles enable row level security;
alter table businesses enable row level security;
alter table orders enable row level security;
alter table campaigns enable row level security;
alter table signatures enable row level security;
alter table checkins enable row level security;
alter table invoices enable row level security;
alter table payouts enable row level security;
alter table events enable row level security;
alter table settings enable row level security;
