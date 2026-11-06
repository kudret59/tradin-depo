"""KUDRET AI local web server. No trading credentials and no order endpoints."""
import json
import os
import sqlite3
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from engine import analyze

ROOT = Path(__file__).resolve().parent
DB = ROOT / "kudret.sqlite3"
STATE = {"status":"idle","updated":None,"error":None,"results":[],"events":[],"scanning":False}
LOCK = threading.Lock()
BASE = "https://api.binance.com"
HEADERS = {"User-Agent":"KUDRET-AI-Research/1.0"}
def fetch_json(path):
    req = urllib.request.Request(BASE + path, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=12) as response:
        return json.load(response)

def db_init():
    with sqlite3.connect(DB) as db:
        db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, ts INTEGER, agent TEXT, message TEXT)")
def event(agent, message):
    item = {"time":int(time.time()),"agent":agent,"message":message}
    with LOCK:
        STATE["events"] = ([item] + STATE["events"])[:80]
    with sqlite3.connect(DB, timeout=10) as db:
        db.execute("INSERT INTO events(ts,agent,message) VALUES(?,?,?)",(item["time"],agent,message))
def scan():
    try:
        with LOCK:
            STATE["status"]="scanning"
            STATE["error"]=None
        event("Orkestratör","Binance spot evreni sorgulanıyor")
        info = fetch_json("/api/v3/exchangeInfo")
        tickers = fetch_json("/api/v3/ticker/24hr")
        eligible = {s["symbol"] for s in info["symbols"] if s.get("status")=="TRADING" and s.get("quoteAsset")=="USDT" and s.get("isSpotTradingAllowed",False) and not s["symbol"].endswith(("UPUSDT","DOWNUSDT","BULLUSDT","BEARUSDT"))}
        ranked = sorted((t for t in tickers if t.get("symbol") in eligible),key=lambda x:float(x.get("quoteVolume",0)),reverse=True)
        results=[]
        for t in ranked[:25]:
            symbol=t["symbol"]
            try:
                raw=fetch_json(f"/api/v3/klines?symbol={symbol}&interval=4h&limit=101")
                now=int(time.time()*1000)
                closed=[c for c in raw if int(c[6]) < now]
                report=analyze(symbol,closed)
                results.append(report)
                event("Coin Avcısı",f"{symbol}: {report['score']}/100 — {report['signal']}")
            except (ValueError,KeyError,IndexError,urllib.error.URLError) as ex:
                event("Veri Denetçisi",f"{symbol} atlandı: {str(ex)[:100]}")
            time.sleep(.12)
        results.sort(key=lambda x:x["score"],reverse=True)
        with LOCK:
            STATE.update(status="ready",updated=int(time.time()),results=results)
        event("Baş Asistan",f"{len(results)} parite analiz edildi; gerçek emir gönderilmedi")
    except Exception as ex:
        with LOCK:
            STATE.update(status="error",error=f"{type(ex).__name__}: {str(ex)[:220]}")
        event("Bağlantı Denetçisi","Piyasa bağlantısı başarısız; sahte fiyat kullanılmadı")
    finally:
        with LOCK:
            STATE["scanning"]=False

class Handler(BaseHTTPRequestHandler):
    def send(self,code,content,mime="application/json; charset=utf-8"):
        body=content.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type",mime)
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        path=urlparse(self.path).path
        if path in ("/","/index.html"):
            return self.send(200,(ROOT/"web"/"index.html").read_text(encoding="utf-8"),"text/html; charset=utf-8")
        if path=="/api/status":
            with LOCK:
                payload={k:(v.copy() if isinstance(v,list) else v) for k,v in STATE.items()}
            return self.send(200,json.dumps(payload,ensure_ascii=False))
        if path=="/api/health":
            return self.send(200,'{"ok":true,"mode":"paper-only"}')
        return self.send(404,'{"error":"not found"}')
    def do_POST(self):
        if urlparse(self.path).path!="/api/scan":
            return self.send(404,'{"error":"not found"}')
        # Localhost-only; before public deployment implement authentication + CSRF protection.
        if self.client_address[0] not in ("127.0.0.1","::1"):
            return self.send(403,'{"error":"local access only"}')
        with LOCK:
            if STATE["scanning"]:
                return self.send(409,'{"error":"scan already running"}')
            STATE["scanning"]=True
        threading.Thread(target=scan,daemon=True).start()
        return self.send(202,'{"started":true}')
if __name__=="__main__":
    db_init()
    port=int(os.getenv("PORT","8765"))
    print(f"KUDRET AI: http://localhost:{port} (paper-only)")
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()
