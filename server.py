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
from agent_runtime import ResearchDesk
from paper_broker import PaperBroker
from paper_scheduler import PaperScheduler
from binance_tr import symbols as tr_symbols, klines as tr_klines
from llm_local import assess as llm_assess

ROOT = Path(__file__).resolve().parent
DB = ROOT / "kudret.sqlite3"
STATE = {"status":"idle","updated":None,"error":None,"results":[],"events":[],"scanning":False}
LOCK = threading.Lock()
DESK = None
BROKER = None
SCHEDULER = None
LLM_STATE = {"status":"idle","last_report":None,"error":None}
QUOTE_TS = {}
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
        event("Orkestratör","Binance TR TRY pariteleri sorgulanıyor")
        markets=tr_symbols()
        if not markets:
            raise ValueError("Binance TR returned no eligible TRY spot markets")
        results=[]
        max_pairs=max(1,min(int(os.getenv("KUDRET_SCAN_LIMIT","25")),200))
        for market in markets[:max_pairs]:
            symbol=market["symbol"].replace("_","")
            try:
                closed=tr_klines(market)
                report=analyze(symbol,closed)
                report["market_symbol"]=market["symbol"]
                report["quote_asset"]="TRY"
                report["exchange"]="Binance TR"
                results.append(report)
                QUOTE_TS[symbol]=time.time()
                event("Coin Avcısı",f"{symbol}: {report['score']}/100 — {report['signal']}")
            except (ValueError,KeyError,IndexError,urllib.error.URLError) as ex:
                event("Veri Denetçisi",f"{symbol} atlandı: {str(ex)[:100]}")
            time.sleep(.15)
        if not results:
            raise ValueError("No validated Binance TR candles; paper trading suspended")
        results.sort(key=lambda x:x["score"],reverse=True)
        if os.getenv("KUDRET_AUTO_LLM")=="1":
            LLM_STATE["status"]="running"
            try:
                snapshot={"market":"Binance TR TRY","candidates":results[:5]}
                LLM_STATE["last_report"]=llm_assess(snapshot)
                LLM_STATE["status"]="done"
                LLM_STATE["error"]=None
                event("Yerel AI", "Piyasa araştırma raporu hazır; emir yetkisi yok")
            except Exception as exc:
                LLM_STATE["status"]="failed"
                LLM_STATE["error"]=f"{type(exc).__name__}: {str(exc)[:160]}"
                event("Yerel AI", "Model bağlantısı başarısız; analiz raporu üretilmedi")
        quotes={r["symbol"]:(r["price"],QUOTE_TS[r["symbol"]]) for r in results}
        for closed in BROKER.check_exits(quotes):
            event("Sanal İşlem",f"Pozisyon kapandı: {closed}")
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
        if path=="/api/llm":
            return self.send(200,json.dumps(LLM_STATE,ensure_ascii=False))
        if path=="/api/paper":
            with LOCK:
                prices={r["symbol"]:r["price"] for r in STATE["results"]}
            return self.send(200,json.dumps(BROKER.snapshot(prices),ensure_ascii=False))
        if path=="/api/agents":
            return self.send(200,json.dumps(DESK.snapshot(),ensure_ascii=False))
        if path=="/api/health":
            return self.send(200,'{"ok":true,"mode":"paper-only"}')
        return self.send(404,'{"error":"not found"}')
    def do_POST(self):
        endpoint=urlparse(self.path).path
        if endpoint not in ("/api/scan","/api/research"):
            return self.send(404,'{"error":"not found"}')
        # Localhost-only; before public deployment implement authentication + CSRF protection.
        if self.client_address[0] not in ("127.0.0.1","::1"):
            return self.send(403,'{"error":"local access only"}')
        if endpoint=="/api/research":
            started=DESK.start()
            return self.send(202 if started else 409,json.dumps({"started":started}))
        with LOCK:
            if STATE["scanning"]:
                return self.send(409,'{"error":"scan already running"}')
            STATE["scanning"]=True
        threading.Thread(target=scan,daemon=True).start()
        return self.send(202,'{"started":true}')
if __name__=="__main__":
    db_init()
    DESK=ResearchDesk(DB)
    BROKER=PaperBroker(DB)
    if os.getenv("KUDRET_AUTO_SCAN")=="1":
        SCHEDULER=PaperScheduler(scan,lambda: dict(STATE),BROKER,event,int(os.getenv("KUDRET_SCAN_INTERVAL","300")))
        SCHEDULER.start()
    port=int(os.getenv("PORT","8765"))
    print(f"KUDRET AI: http://localhost:{port} (paper-only)")
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()
