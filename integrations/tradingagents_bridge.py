"""Optional bridge to the independently installed TradingAgents framework.

No orders are placed. Import and model initialization occur only on explicit invocation.
The framework must be installed from its audited upstream source, with credentials
configured separately. Outputs are research opinions, not validated probabilities.
"""
import argparse
import json
import os
import re
from datetime import date

VALID_SYMBOL = re.compile(r"^[A-Z0-9]{2,20}$")
def validate(symbol, day):
    symbol=symbol.strip().upper()
    if not VALID_SYMBOL.fullmatch(symbol):
        raise ValueError("Invalid ticker format")
    d=date.fromisoformat(day)
    if d>date.today():
        raise ValueError("Future dates not permitted")
    return symbol, d.isoformat()
def run(symbol, day, analysts=("market","social","news","fundamentals")):
    symbol,day=validate(symbol,day)
    if os.getenv("KUDRET_ENABLE_LLM_RESEARCH")!="1":
        raise RuntimeError("LLM research disabled: set KUDRET_ENABLE_LLM_RESEARCH=1 after configuring provider credentials")
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.graph.trading_graph import TradingAgentsGraph
    except ImportError as exc:
        raise RuntimeError("TradingAgents dependency not installed; see integrations/README.md") from exc
    config=DEFAULT_CONFIG.copy()
    # Keep all framework-generated files in a dedicated project workspace.
    config["results_dir"]=os.path.abspath("tradingagents_results")
    config["data_cache_dir"]=os.path.abspath("tradingagents_cache")
    graph=TradingAgentsGraph(selected_analysts=list(analysts),debug=False,config=config)
    _,decision=graph.propagate(symbol,day)
    return {"symbol":symbol,"date":day,"decision":str(decision),"type":"LLM_RESEARCH_ONLY","order_sent":False,"note":"Not a trade recommendation; verify cryptocurrency symbol/data provider compatibility."}
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--symbol",required=True)
    parser.add_argument("--date",default=date.today().isoformat())
    args=parser.parse_args()
    print(json.dumps(run(args.symbol,args.date),ensure_ascii=False,indent=2))
