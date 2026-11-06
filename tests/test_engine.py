import unittest
from engine import ema,rsi,analyze

def candles():
    return [[i*4,1,102,95,100+i*.01,1000+i*3,i*4+3] for i in range(100)]
class EngineTests(unittest.TestCase):
    def test_ema_constant(self):
        self.assertEqual(ema([10]*30,20)[-1],10)
    def test_rsi_flat(self):
        self.assertEqual(rsi([10]*20),50)
    def test_short_rejected(self):
        with self.assertRaises(ValueError): analyze("TEST",candles()[:10])
    def test_report(self):
        report=analyze("TEST",candles())
        self.assertEqual(report["symbol"],"TEST")
        self.assertEqual(len(report["agents"]),6)
        self.assertTrue(0<=report["score"]<=100)
if __name__=="__main__": unittest.main()
