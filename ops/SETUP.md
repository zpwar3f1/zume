# Zumee 运营系统 · 搭建步骤

目标：数据放在云端的 Postgres（Supabase 免费版），网站表单、签约页、打卡页和定时任务跑在 Cloudflare（免费），后台管理用 NocoDB 装在自己电脑上。全部零成本。

## 第 1 步 · 建数据库（你来做，10 分钟）

1. 注册 https://supabase.com ，New project，名字 `zumee`，Region 选 **Canada (Central)** 或 **US West (Oregon)**，数据库密码记下来。
2. 左侧 SQL Editor → New query → 把 `ops/db/schema.sql` 全文粘贴进去 → Run。看到 `Success` 即可。
3. Project Settings → API：记下 `Project URL` 和 `service_role` 密钥（这个密钥只放在 Cloudflare 的环境变量里，绝不放进网页或仓库）。
4. Project Settings → Database → Connection string → **Session pooler** 那一条（家庭网络通常没有 IPv6，直连会连不上），记下来给 NocoDB 用。

## 第 2 步 · 后台管理 NocoDB（你来做，10 分钟）

1. 装 Docker Desktop：https://www.docker.com/products/docker-desktop/ （Mac / Windows 都行）。
2. 在 `ops/nocodb` 目录运行 `docker compose up -d`，打开 http://localhost:8080 ，创建管理员账号。
3. 新建 Base → **Connect External Database** → PostgreSQL，填第 1 步第 4 点的 Session pooler 信息（Host、Port 5432、User `postgres.xxxx`、Password、Database `postgres`，SSL 选 `Required`）。
4. 连上后能看到 drivers / vehicles / businesses / orders / campaigns / checkins / invoices / payouts 这些表。建议建这几个视图：
   - 车主看板：drivers 按 status 分组（new → reviewing → approved → paused）
   - 订单看板：orders 按 status 分组（draft → sent → signed → paid → live → completed）
   - 本周待打卡：视图 v_checkins_due
5. 电脑关了 NocoDB 就打不开，但数据都在 Supabase，不会丢。

## 第 3 步 · Cloudflare 侧（我来做，需要你给一个新的 API token）

在 Cloudflare Dashboard → My Profile → API Tokens → Create Token，权限：
`Account · Cloudflare Pages · Edit`，`Account · Workers Scripts · Edit`，`Account · Workers R2 Storage · Edit`，`Zone · DNS · Edit`（zone 选 zumee.org）。有效期选一个月。

我会用它部署：
- 网站表单改写进 Supabase（替换 Google Sheets）
- 车主打卡页 `/checkin/<token>`，照片存 R2
- 商家签约页 `/sign/<token>` 和车主接受页 `/accept/<token>`，签完自动生成 PDF 存 R2、发邮件、改状态
- 定时任务：每周一提醒拍照、月初月末提醒里程表、月底给商家发月报、发票到期提醒、每天访问一次数据库防止 Supabase 免费项目休眠

## 第 4 步 · 邮件和收款（你来注册）

- https://resend.com 注册，添加域名 zumee.org（我来配 DNS 记录），拿 API key。免费每月 3000 封。
- https://stripe.com 注册公司账号（1376107 B.C. Ltd.），开发票和以后给车主打款都用它。开票免费，e-Transfer 付款手动标记已付不收费。
- 记账用 https://www.waveapps.com ，免费，报 GST 用。

## 状态流转（自动化就是围绕这些状态）

车主 drivers.status：new → reviewing → approved → paused / rejected / left
车辆 vehicles.status：pending → available → booked → inactive
商家 businesses.status：lead → contacted → quoted → signed → active → churned / lost
订单 orders.status：draft → sent（发出签约链接）→ signed → invoiced → paid → in_production → live → completed / cancelled
投放 campaigns.status：invited → accepted / declined / expired → scheduled → installed → live → interrupted → removed → settled
打卡 checkins.status：due → reminded → submitted → ok / rejected / missed
发票 invoices.status：draft → sent → paid / overdue / void
结算 payouts.status：pending → approved → paid / held

## 签约是怎么自动化的

商家：你在 NocoDB 把订单填好，状态改成 `sent` → 系统生成一次性链接发给商家邮箱 → 商家在手机或电脑上看到协议全文和附件 A（已经填好数字）→ 输入姓名职务、手写签名、勾选同意 → 系统记录时间、IP、设备、文本哈希 → 生成签署版 PDF 存 R2，邮件同时发给商家和你 → 状态自动变 `signed` → 自动在 Stripe 开首张发票。

车主：登记通过后，你在 NocoDB 建一条 campaign 并把状态设为 `invited` → 系统发短信或邮件带链接 → 车主看到广告类别、位置、期限、报酬和车主协议 → 点「接受并同意」→ 记录同上，生成 PDF → 状态变 `accepted` → 你安排安装。

两种都符合 BC《电子交易法》对电子签名的要求：能证明是谁、什么时候、同意了哪个版本的文本。
