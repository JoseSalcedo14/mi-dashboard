/**
 * Backend del dashboard - escribe en tu Google Sheet desde el dashboard.
 * Se despliega como Web App (Implementar -> Nueva implementacion -> Aplicacion web).
 * Debe estar ENLAZADO al Sheet (crealo desde Extensiones -> Apps Script dentro del Sheet).
 *
 * Columnas del Sheet (fila 1 = encabezados): section | title | meta | value | status
 */

function sheet_() {
  return SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
}

function doGet() {
  return ContentService
    .createTextOutput(JSON.stringify(readAll_()))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var res = { ok: false };
  try {
    var body = JSON.parse(e.postData.contents);
    var sh = sheet_();
    if (body.op === "add") {
      var r = body.row || {};
      sh.appendRow([body.section, r.title || "", r.meta || "", r.value || "", r.status || ""]);
      res.ok = true;
    } else if (body.op === "delete") {
      var data = sh.getDataRange().getValues();
      for (var i = data.length - 1; i >= 1; i--) {
        var sec = String(data[i][0]).trim().toLowerCase();
        var title = String(data[i][1]).trim();
        if (sec === String(body.section).trim().toLowerCase() && title === String(body.match).trim()) {
          sh.deleteRow(i + 1);
          res.ok = true;
          break;
        }
      }
    } else if (body.op === "update") {
      var d = sh.getDataRange().getValues();
      for (var j = 1; j < d.length; j++) {
        var s = String(d[j][0]).trim().toLowerCase();
        var t = String(d[j][1]).trim();
        if (s === String(body.section).trim().toLowerCase() && t === String(body.match).trim()) {
          var nr = body.row || {};
          sh.getRange(j + 1, 1, 1, 5).setValues([[body.section, nr.title || t, nr.meta || "", nr.value || "", nr.status || ""]]);
          res.ok = true;
          break;
        }
      }
    }
  } catch (err) {
    res.error = String(err);
  }
  return ContentService
    .createTextOutput(JSON.stringify(res))
    .setMimeType(ContentService.MimeType.JSON);
}

function readAll_() {
  var data = sheet_().getDataRange().getValues();
  var out = { tareas: [], finanzas: [], metricas: [] };
  for (var i = 1; i < data.length; i++) {
    var sec = String(data[i][0]).trim().toLowerCase();
    var obj = { title: data[i][1], meta: data[i][2], value: data[i][3], status: data[i][4] };
    if (sec === "tareas" || sec === "tasks") out.tareas.push(obj);
    else if (sec === "finanzas" || sec === "finance") out.finanzas.push(obj);
    else if (sec === "metricas" || sec === "metrics") out.metricas.push(obj);
  }
  return out;
}
