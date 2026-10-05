import json
from urllib.request import Request, urlopen

API_URL = "https://api.gold-api.com/price/XAU"


def fetch_gold_price():
    request = Request(
        API_URL,
        headers={
            "Accept": "application/json",
            "User-Agent": "gold-price-monitor/0.1",
        },
    )

    with urlopen(request, timeout=20) as response:
        return json.load(response)
