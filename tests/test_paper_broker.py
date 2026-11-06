import tempfile,unittest,time
from pathlib import Path
from paper_broker import PaperBroker
class BrokerTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.b=PaperBroker(Path(self.temp.name)/"paper.sqlite3")
 def tearDown(self):self.temp.cleanup()
 def test_round_trip(self):
  now=time.time();self.b.open("BTCUSDT",100,95,110,now)
  self.assertEqual(len(self.b.snapshot()["positions"]),1)
  self.b.close("BTCUSDT",110,now)
  self.assertEqual(len(self.b.snapshot()["fills"]),2)
 def test_stale(self):
  with self.assertRaises(ValueError):self.b.open("BTCUSDT",100,95,110,1)
 def test_max_positions(self):
  now=time.time()
  for s in ("AAA","BBB","CCC"):self.b.open(s,100,95,110,now)
  with self.assertRaises(ValueError):self.b.open("DDD",100,95,110,now)
 def test_invalid_stop(self):
  with self.assertRaises(ValueError):self.b.open("AAA",100,101,110,time.time())
if __name__=="__main__":unittest.main()
