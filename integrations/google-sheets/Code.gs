/**
 * Zumee 表单接收脚本（Google Apps Script）
 * 作用：接收网站的司机登记和商家投放需求，写入本表格的 Drivers / Businesses 两个工作表；
 *      司机上传的车辆照片保存到 Google Drive 的 "Zumee uploads" 文件夹，并在表格里放链接；
 *      每次提交给表格所有者发一封提醒邮件（可关闭）。
 *
 * 部署步骤见同目录 README.md。
 */
const SHEET_DRIVERS = 'Drivers';
const SHEET_BUSINESSES = 'Businesses';
const FOLDER_NAME = 'Zumee uploads';
const NOTIFY = true;               // 每次提交发邮件提醒；不需要改成 false
const NOTIFY_EMAIL = '';           // 留空 = 发给表格所有者

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents || '{}');
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let photoUrl = '';
    if (data.photo) {
      const m = String(data.photo).match(/^data:(image\/[\w.+-]+);base64,(.+)$/);
      if (m) {
        const ext = m[1].split('/')[1].replace('jpeg', 'jpg');
        const name = 'zumee-' + Utilities.formatDate(new Date(), 'America/Vancouver', 'yyyyMMdd-HHmmss') + '-' + (data.phone || 'car').replace(/\D/g, '') + '.' + ext;
        const blob = Utilities.newBlob(Utilities.base64Decode(m[2]), m[1], name);
        const file = getFolder_().createFile(blob);
        photoUrl = file.getUrl();
      }
    }
    let sheet, row;
    if (data.type === 'driver') {
      sheet = getSheet_(ss, SHEET_DRIVERS, ['提交时间 Submitted', '语言 Lang', '居住社区 Area', '车辆品牌 Make', '车辆年份 Year', '月里程 km/month', '电话 Phone', '车辆照片 Photo', '来源页 Page', 'User agent']);
      row = [new Date(), data.lang, data.area, data.brand, data.year, data.mileage, data.phone, photoUrl, data.page, data.ua];
    } else {
      sheet = getSheet_(ss, SHEET_BUSINESSES, ['提交时间 Submitted', '语言 Lang', '商品/店面 Business', '商家地址 Address', '车辆数 Vehicles', '投放月数 Months', '电话 Phone', '来源页 Page', 'User agent']);
      row = [new Date(), data.lang, data.product, data.address, data.vehicles, data.months, data.phone, data.page, data.ua];
    }
    sheet.appendRow(row);
    if (NOTIFY) notify_(data, photoUrl, ss.getUrl());
    return out_({ ok: true });
  } catch (err) {
    return out_({ ok: false, error: String(err) });
  }
}

function doGet() { return out_({ ok: true, service: 'zumee-forms' }); }

function out_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
function getSheet_(ss, name, headers) {
  let sh = ss.getSheetByName(name);
  if (!sh) { sh = ss.insertSheet(name); sh.appendRow(headers); sh.setFrozenRows(1); sh.getRange(1, 1, 1, headers.length).setFontWeight('bold'); }
  return sh;
}
function getFolder_() {
  const it = DriveApp.getFoldersByName(FOLDER_NAME);
  return it.hasNext() ? it.next() : DriveApp.createFolder(FOLDER_NAME);
}
function notify_(data, photoUrl, sheetUrl) {
  try {
    const to = NOTIFY_EMAIL || Session.getEffectiveUser().getEmail();
    const isDriver = data.type === 'driver';
    const subject = (isDriver ? '[Zumee] 新司机登记 ' : '[Zumee] 新商家需求 ') + (data.phone || '');
    const lines = isDriver
      ? ['社区: ' + data.area, '车辆: ' + data.brand + ' ' + data.year, '月里程: ' + data.mileage + ' km', '电话: ' + data.phone, '照片: ' + (photoUrl || '无')]
      : ['商品/店面: ' + data.product, '地址: ' + (data.address || '未填'), '车辆数: ' + data.vehicles, '月数: ' + data.months, '电话: ' + data.phone];
    MailApp.sendEmail(to, subject, lines.join('\n') + '\n\n表格: ' + sheetUrl);
  } catch (e) { /* 邮件失败不影响写入 */ }
}
