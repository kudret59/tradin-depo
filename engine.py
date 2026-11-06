"""Deterministic, explainable research agents. Never places orders."""
from statistics import mean

def ema(values, span):
    if not values:
        return []
    alpha = 2 / (span + 1)
    result = [float(values[0])]
    for value in values[1:]:
        result.append(alpha * float(value) + (1 - alpha) * result[-1])
    return result

def rsi(values, period=14):
    if len(values) <= period:
        return None
    changes = [values[i] - values[i - 1] for i in range(1, len(values))]
    gains = [max(0, x) for x in changes]
    losses = [max(0, -x) for x in changes]
    avg_gain, avg_loss = mean(gains[-period:]), mean(losses[-period:])
    if avg_gain == avg_loss == 0:
        return 50.0
    if avg_loss == 0:
        return 100.0
    return round(100 - 100 / (1 + avg_gain / avg_loss), 2)

def analyze(symbol, candles):
    """Use only *closed* OHLCV candles; no forward-looking values."""
    if len(candles) < 60:
        raise ValueError("At least 60 closed candles required")
    close = [float(c[4]) for c in candles]
    high = [float(c[2]) for c in candles]
    low = [float(c[3]) for c in candles]
    vol = [float(c[5]) for c in candles]
    if any(v <= 0 for v in close) or any(v < 0 for v in vol):
        raise ValueError("Invalid OHLCV")
    price = close[-1]
    e20, e50 = ema(close, 20)[-1], ema(close, 50)[-1]
    momentum = (price / close[-6] - 1) * 100
    volume_ratio = vol[-1] / max(mean(vol[-21:-1]), 1e-12)
    support, resistance = min(low[-30:]), max(high[-30:])
    near_low = (price / support - 1) <= .08
    rebound = close[-1] > close[-2] > close[-3]
    dip = near_low and rebound
    trend = price > e20 > e50
    volume = volume_ratio >= 1.25
    impulse = 45 <= (rsi(close) or 0) <= 70 and momentum > 0
    breakout = price >= max(high[-21:-1]) and volume
    gates = {"dip_rebound":dip,"trend":trend,"volume":volume,"momentum":impulse,"breakout":breakout}
    score = sum([25 if dip else 0,25 if trend else 0,20 if volume else 0,20 if impulse else 0,10 if breakout else 0])
    risk = "PASS" if support < price and volume_ratio >= .6 else "REJECT"
    agents = [
        {"name":"Dip Avcısı","status":"ONAY" if dip else "BEKLE","detail":f"Destek {support:.8g}; toparlanma {rebound}"},
        {"name":"Trend Uzmanı","status":"ONAY" if trend else "BEKLE","detail":f"EMA20 {e20:.8g} / EMA50 {e50:.8g}"},
        {"name":"Hacim Uzmanı","status":"ONAY" if volume else "BEKLE","detail":f"Hacim oranı {volume_ratio:.2f}x"},
        {"name":"Momentum Uzmanı","status":"ONAY" if impulse else "BEKLE","detail":f"RSI {rsi(close)} / 5 mum %{momentum:.2f}"},
        {"name":"Kırılım Uzmanı","status":"ONAY" if breakout else "BEKLE","detail":f"Direnç {resistance:.8g}"},
        {"name":"Risk Denetçisi","status":risk,"detail":"Gerçek emir yasak; yalnızca araştırma"},
    ]
    return {"symbol":symbol,"price":price,"score":score,"gates":gates,"risk":risk,"support":support,"resistance":resistance,"rsi":rsi(close),"volume_ratio":round(volume_ratio,2),"agents":agents,"signal":"ARAŞTIR" if score >= 75 and risk == "PASS" else "BEKLE"}
