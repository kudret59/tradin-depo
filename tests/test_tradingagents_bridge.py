import importlib.util
import pathlib
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("bridge",ROOT/"integrations"/"tradingagents_bridge.py")
bridge=importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
class BridgeTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(bridge.validate("btc","2026-11-05"),("BTC","2026-11-05"))
    def test_invalid_symbol(self):
        with self.assertRaises(ValueError):bridge.validate("BTC; rm -rf /","2026-11-05")
    def test_future_date(self):
        with self.assertRaises(ValueError):bridge.validate("BTC","2099-01-01")
    def test_disabled(self):
        import os
        original=os.environ.pop("KUDRET_ENABLE_LLM_RESEARCH",None)
        try:
            with self.assertRaises(RuntimeError):bridge.run("BTC","2026-11-05")
        finally:
            if original is not None:os.environ["KUDRET_ENABLE_LLM_RESEARCH"]=original
if __name__=="__main__":unittest.main()
