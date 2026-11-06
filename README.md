# KUDRET AI — Altcoin Hunter Web

Açık kaynak, **paper-only** altcoin araştırma terminali. Modern koyu tema, görev tabanlı ajan masaları, Binance global spot USDT taraması ve açıklanabilir dip/trend/hacim/momentum puanlaması.

## Başlat
Python 3.10+ ile (ek paket gerektirmez):

```bash
python server.py
```

Tarayıcı: http://localhost:8765

## Mimari
- `server.py`: HTTP API, public Binance market data, SQLite görev/araştırma hafızası.
- `engine.py`: Dip-tepe, EMA, RSI, hacim, momentum, risk filtreleri; ayrı uzman raporları.
- `web/index.html`: animasyonlu ajan masaları ve canlı tarama paneli.
- `tests/test_engine.py`: deterministik birim testleri.

**Sınırlar:** Bu ilk sürüm LLM ile kendi kendini eğiten bir sistem değildir. İnternet araştırması otomatik kod çalıştırmaz. Binance global API erişimi ve hosting ortamı ayrıca doğrulanmalıdır. Bu uygulama gerçek emir göndermez, yatırım tavsiyesi değildir. Varsayılan olarak kimlik doğrulaması yoktur: internete açık dağıtım öncesi auth, HTTPS, rate limit ve kalıcı DB gerekir.

## Codex görevi
Bu depoyu Codex Cloud ortamına bağlayın. Sonraki işler: yetkilendirme, WebSocket/stream, Binance TR adaptörü, paper matching engine, out-of-sample backtest, strateji deney veritabanı, güvenli LLM araştırma ajanları ve CI.
