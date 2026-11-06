import unittest
from binance_tr import parse_symbols,unwrap
class TRTests(unittest.TestCase):
 def test_parse(self):
  p={"code":0,"data":{"list":[{"symbol":"BTC_TRY","quoteAsset":"TRY","baseAsset":"BTC","spotTradingEnable":1,"type":1},{"symbol":"BTC_USDT","quoteAsset":"USDT","spotTradingEnable":1,"type":1},{"symbol":"ETH_TRY","quoteAsset":"TRY","spotTradingEnable":0,"type":3}]}}
  self.assertEqual([x["symbol"] for x in parse_symbols(p)],["BTC_TRY"])
 def test_bad_api(self):
  with self.assertRaises(ValueError):unwrap({"code":-1,"data":[]})
if __name__=="__main__":unittest.main()
