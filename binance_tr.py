"""Binance TR public TRY spot market adapter.

Endpoints from https://www.binance.tr/apidocs/
No credentials and no order methods.
"""
import json
import re
import time
import urllib.request
from urllib.parse import urlencode

SYMBOLS_URL="https://www.binance.tr/open/v1/common/symbols"
KLINE_HOSTS={1:"https://api.binance.me/api/v1/klines",3:"https://cloudme-tr.2meta.app/api/v1/klines"}
VALID=re.compile(r"^[A-Z0-9]{2,30}_[A-Z0-9]{2,12}$")
def get_json(url,timeout=12):
    req=urllib.request.Request(url,headers={"User-Agent":"KUDRET-AI-PaperResearch/1.0","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as response:
        if response.status!=200:
            raise ValueError("Binance TR HTTP error")
        data=response.read(4_000_001)
        if len(data)>4_000_000: raise ValueError("Oversized response")
        return json.loads(data)
def unwrap(payload):
    if not isinstance(payload,dict) or payload.get("code") not in (0,"0"):
        raise ValueError("Binance TR unsuccessful API response")
    if "data" not in payload: raise ValueError("Missing data")
    return payload["data"]
def parse_symbols(payload):
    data=unwrap(payload)
    if not isinstance(data,dict) or not isinstance(data.get("list"),list): raise ValueError("Invalid symbol list")
    output=[]
    for item in data["list"]:
        if not isinstance(item,dict): continue
        symbol=item.get("symbol","")
        if (item.get("quoteAsset")!="TRY" or not VALID.fullmatch(symbol)
            or int(item.get("spotTradingEnable",0))!=1): continue
        typ=int(item.get("type",0))
        if typ not in KLINE_HOSTS: continue
        output.append({"symbol":symbol,"type":typ,"base":item.get("baseAsset",""),"quote":"TRY"})
    return sorted(output,key=lambda x:x["symbol"])
def symbols():
    return parse_symbols(get_json(SYMBOLS_URL))
def klines(market,interval="4h",limit=101):
    symbol=market["symbol"]
    typ=int(market["type"])
    if not VALID.fullmatch(symbol) or typ not in KLINE_HOSTS: raise ValueError("Unsupported symbol/type")
    if interval not in ("1h","4h","1d") or not 60<=limit<=500: raise ValueError("Unsupported candle parameters")
    api_symbol=symbol.replace("_","") if typ==1 else symbol
    url=KLINE_HOSTS[typ]+"?"+urlencode({"symbol":api_symbol,"interval":interval,"limit":limit})
    data=unwrap(get_json(url))
    if not isinstance(data,list): raise ValueError("Invalid candle list")
    now=int(time.time()*1000)
    candles=[c for c in data if isinstance(c,list) and len(c)>=7 and int(c[6])<now]
    if len(candles)<60: raise ValueError("Not enough closed candles")
    if any(int(candles[i][0])>=int(candles[i+1][0]) for i in range(len(candles)-1)):
        raise ValueError("Unsorted candles")
    return candles
