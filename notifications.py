import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


def load_credentials():
    path = (
        Path.home()
        / ".config"
        / "gold-price-monitor"
        / "credentials.json"
    )
    with path.open() as file:
        credentials = json.load(file)

    for key in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
        value = credentials.get(key)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Missing credential: {key}")

        os.environ[key] = value.strip()

def send_telegram_alert(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    if not token or not chat_id:
        raise ValueError("Telegram token or chat ID is missing.")

    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
    }).encode("utf-8")

    request = Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=20) as response:
        result = json.load(response)

    if not result.get("ok"):
        raise ValueError("Telegram did not accept the alert.")

    print("Telegram alert sent.")
