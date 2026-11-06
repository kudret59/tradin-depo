"""Background paper research scheduler. Disabled unless explicitly enabled.

No real exchange order endpoints. Only fresh closed-candle signals are considered.
"""
import os
import threading
import time

class PaperScheduler:
    def __init__(self,scan_fn,status_fn,broker,event_fn,interval=300):
        self.scan_fn=scan_fn
        self.status_fn=status_fn
        self.broker=broker
        self.event_fn=event_fn
        self.interval=max(60,int(interval))
        self.stop_event=threading.Event()
        self.last_entry={}
        self.thread=None
    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread=threading.Thread(target=self._loop,daemon=True,name="paper-scheduler")
        self.thread.start()
    def stop(self):
        self.stop_event.set()
    def _loop(self):
        while not self.stop_event.is_set():
            try:
                self.scan_fn()
                if os.getenv("KUDRET_AUTO_PAPER")=="1":
                    self.evaluate(self.status_fn())
            except Exception as exc:
                self.event_fn("Paper Scheduler",f"Error: {type(exc).__name__}: {str(exc)[:100]}")
            self.stop_event.wait(self.interval)
    def evaluate(self,state,now=None):
        now=time.time() if now is None else now
        if state.get("status")!="ready" or not state.get("updated") or now-state["updated"]>300:
            return []
        if state.get("scanning"):
            return []
        active={p["symbol"] for p in self.broker.snapshot()["positions"]}
        opened=[]
        for r in state.get("results",[]):
            if len(active)>=3:
                break
            symbol=r.get("symbol","")
            price=r.get("price",0)
            support=r.get("support",0)
            if symbol in active or now-self.last_entry.get(symbol,0)<86400:
                continue
            gates=r.get("gates",{})
            if (r.get("risk")!="PASS" or r.get("score",0)<80
                or not all(gates.get(k,False) for k in ("trend","volume","momentum"))
                or not (gates.get("dip_rebound") or gates.get("breakout"))
                or not 0<support<price or (price-support)/price>.08):
                continue
            try:
                trade=self.broker.open(symbol,price,support,price+2*(price-support),state["updated"])
                self.last_entry[symbol]=now
                active.add(symbol)
                opened.append(trade)
                self.event_fn("Paper Execution",f"Paper BUY {symbol}: {trade['qty']:.6g} @ {trade['fill']:.8g}")
            except ValueError as exc:
                self.event_fn("Risk Officer",f"Rejected {symbol}: {str(exc)[:80]}")
        return opened
