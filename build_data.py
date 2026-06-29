#!/usr/bin/env python3
import os, json, urllib.request, csv, io, datetime, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data.json")
DAYS = {0:"lun",1:"mar",2:"mié",3:"jue",4:"vie",5:"sáb",6:"dom"}
MONTHS = {1:"ene",2:"feb",3:"mar",4:"abr",5:"may",6:"jun",7:"jul",8:"ago",9:"sep",10:"oct",11:"nov",12:"dic"}

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "dashboard-bot"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def epoch(x):
    if isinstance(x, datetime.datetime):
        return x.timestamp() if x.tzinfo else x.replace(tzinfo=datetime.timezone.utc).timestamp()
    return datetime.datetime(x.year, x.month, x.day, tzinfo=datetime.timezone.utc).timestamp()

def get_calendar(ics_text, max_items=6, days_ahead=14):
    import recurring_ical_events
    from icalendar import Calendar
    cal = Calendar.from_ical(ics_text)
    now = datetime.datetime.now(datetime.timezone.utc)
    start = now - datetime.timedelta(hours=3); end = now + datetime.timedelta(days=days_ahead)
    items = []
    for e in recurring_ical_events.of(cal).between(start, end):
        summary = str(e.get("SUMMARY", "(sin título)")); dt = e.get("DTSTART").dt
        if isinstance(dt, datetime.datetime):
            meta = f"{DAYS[dt.weekday()]} {dt.day} {MONTHS[dt.month]}, {dt.strftime('%H:%M')}"
        else:
            meta = f"{DAYS[dt.weekday()]} {dt.day} {MONTHS[dt.month]} · todo el día"
        items.append((epoch(dt), {"title": summary, "meta": meta}))
    items.sort(key=lambda x: x[0])
    print(f"  Calendario: {len(items)} evento(s)")
    return [i[1] for i in items[:max_items]]

def parse_sheet(text):
    tasks, fin, met = [], [], []
    for row in csv.DictReader(io.StringIO(text)):
        sec = (row.get("section") or "").strip().lower()
        if sec in ("tareas","tasks"):
            tasks.append({"title":row.get("title",""),"meta":row.get("meta",""),"status":(row.get("status") or "ok").strip() or "ok","due":row.get("value","")})
        elif sec in ("finanzas","finance"):
            amt=(row.get("value") or "").strip(); fin.append({"label":row.get("title",""),"amount":amt,"pos":not amt.startswith("-")})
        elif sec in ("metricas","métricas","metrics"):
            pct=re.sub(r"[^\d.]","",row.get("meta","") or "0"); met.append({"k":row.get("title",""),"v":row.get("value",""),"pct":int(float(pct)) if pct else 0})
    return tasks, fin, met

def main():
    data = json.load(open(DATA, encoding="utf-8"))
    cal_url = os.getenv("CAL_ICS_URL","").strip()
    if cal_url:
        try: data["calendar"] = get_calendar(fetch(cal_url))
        except Exception as e: print("  Calendar error:", repr(e))
    sheet_url = os.getenv("SHEET_CSV_URL","").strip()
    if sheet_url:
        try:
            t,f,m = parse_sheet(fetch(sheet_url))
            if t: data["tasks"]=t
            if f: data["finance"]["rows"]=f
            if m: data["metrics"]=m
        except Exception as e: print("  Sheet error:", repr(e))
    data["updated"] = datetime.datetime.now().strftime("%d %b %Y, %H:%M") + " UTC"
    json.dump(data, open(DATA,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print("data.json actualizado:", data["updated"])

if __name__ == "__main__":
    main()
