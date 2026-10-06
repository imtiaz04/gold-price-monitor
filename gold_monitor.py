import sqlite3
import sys
from datetime import datetime
from urllib.error import HTTPError, URLError
from zoneinfo import ZoneInfo


from database import (
    DB_PATH,
    save_reading,
    get_pending_alerts,
    mark_alert_sent,
)
from notifications import load_credentials, send_telegram_alert
from price_api import fetch_gold_price

ALERT_THRESHOLD_USD = 1.0

def deliver_pending_alerts():
    for alert_id, message in get_pending_alerts("USA"):
        print(f"Delivering queued alert #{alert_id}")
        send_telegram_alert(message)
        mark_alert_sent(alert_id)
   
def main():
    try:
        load_credentials()
        deliver_pending_alerts()
        data = fetch_gold_price()
       

        if data["symbol"] != "XAU" or data["currency"] != "USD":
            raise ValueError("Expected gold priced in USD.")

        price = float(data["price"])
        if not 0 < price < float("inf"):
            raise ValueError("Received an invalid price.")

        updated_at = datetime.fromisoformat(
            data["updatedAt"].replace("Z", "+00:00")
        )
        local_time = updated_at.astimezone(
            ZoneInfo("America/New_York")
        )     

        print(f"Gold price: ${price:,.2f} USD per troy ounce")
        print(f"Source updated: {local_time:%Y-%m-%d %I:%M:%S %p %Z}")

        previous, saved = save_reading(
            price, updated_at, ALERT_THRESHOLD_USD
        )
        
        if not saved:
            print("No newer source update; reading skipped.")
        elif previous is None:
            print("First reading saved. Baseline established.")
        else:
            change = price - previous[0]
            percentage = (change / previous[0]) * 100

            print(f"Previous price: ${previous[0]:,.2f}")
            print(
                f"Change since previous reading: "
                f"${change:+,.2f} ({percentage:+.3f}%)"
            )

        deliver_pending_alerts()
        print(f"Database: {DB_PATH}")

    except (
        HTTPError,
        URLError,
        TimeoutError,
        ValueError,
        KeyError,
        TypeError,
        sqlite3.Error,
        OSError,
    ) as error:
        print(f"Gold price check failed: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
