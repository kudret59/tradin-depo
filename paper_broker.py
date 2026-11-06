"""Persistent paper-only broker; no real orders, no API credentials."""
import sqlite3,time,math
class PaperBroker:
 def __init__(self,path):
  self.path=str(path)
  with sqlite3.connect(self.path) as db:
   db.execute("CREATE TABLE IF NOT EXISTS account(id INTEGER PRIMARY KEY,cash REAL)")
   db.execute("INSERT OR IGNORE INTO account VALUES(1,10000)")
   db.execute("CREATE TABLE IF NOT EXISTS positions(symbol TEXT PRIMARY KEY,qty REAL,entry REAL,stop REAL,target REAL)")
   db.execute("CREATE TABLE IF NOT EXISTS fills(id INTEGER PRIMARY KEY,ts INTEGER,symbol TEXT,side TEXT,qty REAL,price REAL,fee REAL,pnl REAL)")
 def snapshot(self,prices=None):
  with sqlite3.connect(self.path) as db:
   cash=db.execute("SELECT cash FROM account").fetchone()[0]
   ps=[dict(zip(("symbol","qty","entry","stop","target"),r)) for r in db.execute("SELECT * FROM positions")]
   fills=[dict(zip(("ts","symbol","side","qty","price","fee","pnl"),r)) for r in db.execute("SELECT ts,symbol,side,qty,price,fee,pnl FROM fills ORDER BY id DESC LIMIT 50")]
  return {"cash":round(cash,2),"equity_estimate":round(cash+sum(p["qty"]*(prices or {}).get(p["symbol"],p["entry"]) for p in ps),2),"positions":ps,"fills":fills,"mode":"PAPER_ONLY"}
 def open(self,symbol,price,stop,target,quote_ts):
  now=time.time()
  if now-quote_ts>300 or quote_ts>now+30: raise ValueError("Stale quote")
  if not symbol.isalnum() or not all(map(math.isfinite,(price,stop,target))) or not 0<stop<price<target: raise ValueError("Invalid entry/stop/target")
  fill=price*1.0005
  with sqlite3.connect(self.path,timeout=15) as db:
   db.execute("BEGIN IMMEDIATE")
   cash=db.execute("SELECT cash FROM account").fetchone()[0]
   rows=db.execute("SELECT symbol,qty,entry FROM positions").fetchall()
   if len(rows)>=3 or symbol in [r[0] for r in rows]: raise ValueError("Max 3 positions or duplicate")
   equity=cash+sum(q*p for _,q,p in rows)
   qty=min(equity*.01/(fill-stop),cash*.25/(fill*1.001))
   if qty<=0: raise ValueError("No paper funds")
   fee=qty*fill*.001
   db.execute("UPDATE account SET cash=cash-?",(qty*fill+fee,))
   db.execute("INSERT INTO positions VALUES(?,?,?,?,?)",(symbol,qty,fill,stop,target))
   db.execute("INSERT INTO fills(ts,symbol,side,qty,price,fee,pnl) VALUES(?,?,?,?,?,?,0)",(int(now),symbol,"BUY",qty,fill,fee))
  return {"symbol":symbol,"qty":qty,"fill":fill,"fee":fee}
 def close(self,symbol,price,quote_ts):
  now=time.time()
  if now-quote_ts>300 or quote_ts>now+30 or not math.isfinite(price) or price<=0: raise ValueError("Stale/invalid quote")
  with sqlite3.connect(self.path,timeout=15) as db:
   db.execute("BEGIN IMMEDIATE")
   row=db.execute("SELECT qty,entry FROM positions WHERE symbol=?",(symbol,)).fetchone()
   if not row: raise ValueError("Position not found")
   qty,entry=row;fill=price*.9995;fee=qty*fill*.001;pnl=qty*(fill-entry)-fee-qty*entry*.001
   db.execute("UPDATE account SET cash=cash+?",(qty*fill-fee,))
   db.execute("DELETE FROM positions WHERE symbol=?",(symbol,))
   db.execute("INSERT INTO fills(ts,symbol,side,qty,price,fee,pnl) VALUES(?,?,?,?,?,?,?)",(int(now),symbol,"SELL",qty,fill,fee,pnl))
  return {"symbol":symbol,"realized_pnl":round(pnl,4)}
 def check_exits(self,quotes):
  result=[]
  for p in self.snapshot()["positions"]:
   q=quotes.get(p["symbol"])
   if q and (q[0]<=p["stop"] or q[0]>=p["target"]):
    try: result.append(self.close(p["symbol"],*q))
    except ValueError: pass
  return result
