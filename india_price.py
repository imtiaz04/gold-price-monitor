import html
import re
from urllib.request import Request, urlopen
from datetime import datetime


API_URL = "https://www.goodreturns.in/gold-rates/hyderabad.html"


def _extract_price(page, element_id):
    pattern = rf'id="{re.escape(element_id)}"[^>]*>(.*?)</span>'
    match = re.search(pattern, page, re.IGNORECASE | re.DOTALL)

    if not match:
        raise ValueError(f"Could not find {element_id}")

    value = html.unescape(match.group(1))
    value = re.sub(r"<[^>]+>", "", value)
    value = value.replace("₹", "").replace(",", "").strip()

    return int(value)

def _extract_source_date(page):
    match = re.search(
        r'Gold Rate in Hyderabad Today \((\d{1,2} [A-Za-z]+ \d{4})\)',
        page,
        re.IGNORECASE,
    )

    if not match:
        raise ValueError("Could not find Hyderabad source date")

    source_date = datetime.strptime(
        match.group(1),
        "%d %B %Y",
    )

    return source_date.date().isoformat()


def fetch_hyderabad_gold_price():
    request = Request(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
        },
    )

    with urlopen(request, timeout=20) as response:
        page = response.read().decode("utf-8", errors="ignore")

    price_24k_per_gram = _extract_price(page, "24K-price")
    price_22k_per_gram = _extract_price(page, "22K-price")
    source_date = _extract_source_date(page)

    return {
        "city": "Hyderabad",
        "currency": "INR",
        "24k_per_gram": price_24k_per_gram,
        "22k_per_gram": price_22k_per_gram,
        "24k_per_10g": price_24k_per_gram * 10,
        "22k_per_10g": price_22k_per_gram * 10,
        "source_date": source_date,
        
    }
