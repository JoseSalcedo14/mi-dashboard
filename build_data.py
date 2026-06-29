#!/usr/bin/env python3
"""
Arma data.json para el dashboard SIN APIs ni claves.
Fuentes (todas opcionales, se configuran con variables de entorno):

  CAL_ICS_URL   -> "Dirección secreta en formato iCal" de Google Calendar.
                   (Google Calendar > Configuración del calendario > Integrar calendario)
  SHEET_CSV_URL -> Google Sheet publicado como CSV.
                   (Archivo > Compartir > Publicar en la web > CSV)
                   Columnas esperadas (una fila por dato):
                   section,title,meta,value,status
                   section = tareas | finanzas | metricas

Si una fuente no está configurada, se mantienen los datos de ejemplo de esa sección.
Solo depende de la librería estándar de Python -> corre en cualquier GitHub Action.
"""
import os, json, urllib.request, csv, io, datetime, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data.json")

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "dashboard-bot"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

# ---------- Google Calendar (ICS) ----------
def parse_ics(text, max_items=6):
    events = []
    for block in text.split("BEGIN:VEVENT")[1:]:
        def grab(key):
            m = re.search(r"\n" + key + r"[^:]*:(.+)", block)
            return m.group(1).strip() if m else ""
        summary = grab("SUMMARY")
        start = grab("DTSTART")
        if not summary or not start:
            continue
        dt = parse_dt(start)
        if dt and dt >= datetime.datetime.now() - datetime.timedelta(hours=2):
            events.append((dt, summary))
    events.sort(key=lambda e: e[0])
    out = []
    for dt, summary in events[:max_items]:
        out.append({"title": summary, "meta": dt.strftime("%a %d, %H:%M")})
    return out

def parse_dt(s):
    s = s.strip()
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%dT%H%M%S", "%Y%m%d"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

# ---------- Google Sheet (CSV) ----------
def parse_sheet(text):
    tasks, finance_rows, metrics = [], [], []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        sec = (row.get("section") or "").strip().lower()
        if sec in ("tareas", "tasks"):
            tasks.append({
                "title": row.get("title", ""), "meta": row.get("meta", ""),
                "status": (row.get("status") or "ok").strip() or "ok",
                "due": row.get("value", "")
            })
        elif sec in ("finanzas", "finance"):
            amt = (row.get("value") or "").strip()
            finance_rows.append({"label": row.get("title", ""), "amount": amt,
                                 "pos": not amt.startswith("-")})
        elif sec in ("metricas", "métricas", "metrics"):
            pct = re.sub(r"[^\d.]", "", row.get("meta", "") or "0")
            metrics.append({"k": row.get("title", ""), "v": row.get("value", ""),
                            "pct": int(float(pct)) if pct else 0})
    return tasks, finance_rows, metrics

def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    cal_url = os.getenv("CAL_ICS_URL", "").strip()
    if cal_url:
        try:
            data["calendar"] = parse_ics(fetch(cal_url)) or data["calendar"]
        except Exception as e:
            print("Calendar error:", e)

    sheet_url = os.getenv("SHEET_CSV_URL", "").strip()
    if sheet_url:
        try:
            t, f_rows, m = parse_sheet(fetch(sheet_url))
            if t: data["tasks"] = t
            if f_rows: data["finance"]["rows"] = f_rows
            if m: data["metrics"] = m
        except Exception as e:
            print("Sheet error:", e)

    data["updated"] = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("data.json actualizado:", data["updated"])

if __name__ == "__main__":
    main()
