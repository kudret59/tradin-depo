import tempfile,time,unittest
from pathlib import Path
from paper_broker import PaperBroker
from paper_scheduler import PaperScheduler
class SchedulerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.broker=PaperBroker(Path(self.tmp.name)/"paper.sqlite3")
  self.messages=[]
  self.scheduler=PaperScheduler(lambda:None,lambda:{},self.broker,lambda *args:self.messages.append(args))
 def tearDown(self):self.tmp.cleanup()
 def test_good_signal(self):
  now=time.time()
  signal={"symbol":"BTCUSDT","price":100,"support":96,"score":90,"risk":"PASS","gates":{"trend":True,"volume":True,"momentum":True,"dip_rebound":True}}
  opened=self.scheduler.evaluate({"status":"ready","updated":now,"scanning":False,"results":[signal]},now)
  self.assertEqual(len(opened),1)
  self.assertEqual(len(self.broker.snapshot()["positions"]),1)
 def test_stale(self):
  now=time.time()
  self.assertEqual(self.scheduler.evaluate({"status":"ready","updated":now-600,"results":[]},now),[])
 def test_no_repeat(self):
  now=time.time()
  signal={"symbol":"BTCUSDT","price":100,"support":96,"score":90,"risk":"PASS","gates":{"trend":True,"volume":True,"momentum":True,"breakout":True}}
  state={"status":"ready","updated":now,"scanning":False,"results":[signal]}
  self.scheduler.evaluate(state,now)
  self.assertEqual(self.scheduler.evaluate(state,now+1),[])
if __name__=="__main__":unittest.main()
