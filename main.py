import json
import urllib.request
import urllib.parse

def get_price(symbol):
    url = "https://api.binance.com/api/v3/ticker/price"
    params = urllib.parse.urlencode({"symbol": symbol.upper()})
    request = urllib.request.Request(
        f"{url}?{params}",
        headers={"User-Agent": "CryptoAnalyzer/1.0"}
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))

    return float(data["price"])


def get_candles(symbol, interval="15m"):
    url = "https://api.binance.com/api/v3/klines"
    params = urllib.parse.urlencode({
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": 100
    })

    request = urllib.request.Request(
        f"{url}?{params}",
        headers={"User-Agent": "CryptoAnalyzer/1.0"}
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))

    return [float(candle[4]) for candle in data]


def analyze(symbol):
    prices = get_candles(symbol)

    changes = [
        prices[i] - prices[i - 1]
        for i in range(1, len(prices))
    ]

    gains = [max(change, 0) for change in changes[-14:]]
    losses = [max(-change, 0) for change in changes[-14:]]

    avg_gain = sum(gains) / 14
    avg_loss = sum(losses) / 14

    if avg_loss == 0:
        rsi = 100 if avg_gain > 0 else 50
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    ma20 = sum(prices[-20:]) / 20
    ma50 = sum(prices[-50:]) / 50
    current_price = get_price(symbol)

    if current_price > ma20 and ma20 > ma50:
        trend = "صعودی"
    elif current_price < ma20 and ma20 < ma50:
        trend = "نزولی"
    else:
        trend = "خنثی یا نامشخص"

    if rsi < 30:
        momentum = "اشباع فروش"
    elif rsi > 70:
        momentum = "اشباع خرید"
    else:
        momentum = "متعادل"

    return {
        "symbol": symbol.upper(),
        "price": current_price,
        "trend": trend,
        "rsi": round(rsi, 2),
        "momentum": momentum,
        "ma20": round(ma20, 8),
        "ma50": round(ma50, 8)
    }


if __name__ == "__main__":
    symbol = input("Enter symbol (e.g. XRPUSDT): ").strip()

    try:
        result = analyze(symbol)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as error:
        print("Analysis failed:", error)
