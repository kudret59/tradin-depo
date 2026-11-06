import tempfile
import unittest
from pathlib import Path
from agent_runtime import ResearchDesk
class RuntimeTests(unittest.TestCase):
    def test_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            desk=ResearchDesk(Path(d)/"runtime.sqlite3")
            snapshot=desk.snapshot()
            self.assertFalse(snapshot["running"])
            self.assertGreaterEqual(len(snapshot["agents"]),10)
            self.assertEqual(snapshot["jobs"],[])
    def test_job_persistence(self):
        with tempfile.TemporaryDirectory() as d:
            desk=ResearchDesk(Path(d)/"runtime.sqlite3")
            jid=desk._job("research","test","running")
            desk._job("research","test","done","ok",jid)
            self.assertEqual(desk.snapshot()["jobs"][0]["status"],"done")
if __name__=="__main__":unittest.main()
