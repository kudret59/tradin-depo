"""Agent task coordination and auditable research without private API keys."""
import sqlite3
import threading
import time
from pathlib import Path
from research_agents import AGENTS, ingest, latest

class ResearchDesk:
    def __init__(self, db_path):
        self.db_path=str(db_path)
        self.lock=threading.Lock()
        self.running=False
        self.last_run=0
        self.last_error=None
        self.last_result=None
        with sqlite3.connect(self.db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS agent_jobs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL, task TEXT NOT NULL,
                status TEXT NOT NULL, started_at INTEGER NOT NULL,
                ended_at INTEGER, detail TEXT
            )""")
    def _job(self, agent, task, status, detail="", job_id=None):
        with sqlite3.connect(self.db_path,timeout=15) as db:
            if job_id is None:
                cur=db.execute("INSERT INTO agent_jobs(agent,task,status,started_at,detail) VALUES(?,?,?,?,?)",
                    (agent,task,status,int(time.time()),detail))
                return cur.lastrowid
            db.execute("UPDATE agent_jobs SET status=?,ended_at=?,detail=? WHERE id=?",
                (status,int(time.time()),detail,job_id))
    def start(self):
        with self.lock:
            if self.running:
                return False
            self.running=True
        threading.Thread(target=self._run,daemon=True).start()
        return True
    def _run(self):
        job_id=self._job("research","Collect approved RSS sources","running")
        try:
            result=ingest(self.db_path)
            self._job("research","Collect approved RSS sources","done",str(result),job_id)
            with self.lock:
                self.last_result=result
                self.last_error=None
                self.last_run=int(time.time())
        except Exception as exc:
            message=f"{type(exc).__name__}: {str(exc)[:160]}"
            self._job("research","Collect approved RSS sources","failed",message,job_id)
            with self.lock:
                self.last_error=message
        finally:
            with self.lock:
                self.running=False
    def snapshot(self):
        with self.lock:
            meta={"running":self.running,"last_run":self.last_run,"last_error":self.last_error,"last_result":self.last_result}
        with sqlite3.connect(self.db_path,timeout=15) as db:
            db.row_factory=sqlite3.Row
            jobs=[dict(row) for row in db.execute(
                "SELECT id,agent,task,status,started_at,ended_at,detail FROM agent_jobs ORDER BY id DESC LIMIT 25")]
        return {**meta,"agents":AGENTS,"jobs":jobs,"articles":latest(self.db_path,25)}
