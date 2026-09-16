# 把网站表单接到 Google Sheet

网站的两个表单（司机登记、商家投放需求）会把数据 POST 到一个 Google Apps Script 网页应用，
脚本把数据写进你自己的 Google Sheet，司机照片存到你 Google Drive 的 `Zumee uploads` 文件夹。
数据只经过你的 Google 账号，不经过任何第三方服务。

## 部署（约 5 分钟，只做一次）

1. 打开 https://sheets.new 新建一个表格，起名 `Zumee 报名表`。
2. 菜单 **扩展程序 (Extensions) → Apps Script**。
3. 删掉编辑器里默认的内容，把本目录 `Code.gs` 的全部内容粘贴进去，Ctrl/Cmd+S 保存。
4. 右上角 **部署 (Deploy) → 新建部署 (New deployment)**。
   - 类型：选 **网页应用 (Web app)**
   - 说明：随便填，比如 `zumee forms v1`
   - 执行身份 (Execute as)：**我 (Me)**
   - 谁可以访问 (Who has access)：**任何人 (Anyone)**  ← 必须是 Anyone，网站才能提交
5. 点 **部署**。第一次会弹出授权：选择你的账号 → 点 "Advanced / 高级" → "Go to (unsafe) / 前往" → 允许。
   这是 Google 对所有自建脚本的标准提示，脚本只访问你自己的表格和 Drive。
6. 复制出现的 **网页应用 URL**（形如 `https://script.google.com/macros/s/AKfy.../exec`），发给 Claude 填进网站。

## 验证

部署后在浏览器打开那个 URL，看到 `{"ok":true,"service":"zumee-forms"}` 就说明脚本在线。
网站提交一次后，表格里会自动出现 `Drivers` 和 `Businesses` 两个工作表，第一行是表头。

## 以后改脚本

改完 `Code.gs` 后要 **部署 → 管理部署 → 编辑 → 版本选"新版本" → 部署**，URL 不变。
只保存不重新部署的话，线上还是旧版本。

## 关闭邮件提醒

把 `Code.gs` 顶部的 `NOTIFY` 改成 `false` 后重新部署。
