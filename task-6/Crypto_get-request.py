import json
import time
import urllib.request

COINS = {"BTC": "bitcoin",
         "ETH": "ethereum",
         "USDT": "tether",
         "USDC": "usd-coin",
         "BNB": "binancecoin",
         "SOL": "solana",
         "XRP": "ripple",
         "ADA": "cardano",
         "MATIC": "matic-network",  # несоответствие кода для запроса
         "TON": "the-open-network"
         }

FROM_TS = 1775174400  # 3 апреля 2026 00:00 UTC
TO_TS = 1790985600  # 3 октября 2026 00:00 UTC

BASE_URL = "https://api.coingecko.com/api/v3"


def fetch_history(coin_index, from_ts, to_ts):
    url = f"{BASE_URL}/coins/{coin_index}/market_chart/range?vs_currency=usd&from={from_ts}&to={to_ts}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


all_data = {}
for ticker, coin_id in list(COINS.items())[:5]:
    print(f"Запрос: {ticker} ({coin_id})...")
    data = fetch_history(coin_id, FROM_TS, TO_TS)
    print(data)
    all_data[ticker] = data["prices"]  # список [timestamp_ms, price]
    time.sleep(1.5)  # уважаем rate-limit free-плана

with open("crypto_prices_6m.json", "w") as f:
    json.dump(all_data, f, indent=2)

    print("Готово! Данные сохранены в crypto_prices_6m.json")
