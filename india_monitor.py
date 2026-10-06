
from database import (
    get_pending_alerts,
    mark_alert_sent,
    save_india_reading,
)
from india_price import fetch_hyderabad_gold_price
from notifications import load_credentials, send_telegram_alert


def deliver_pending_alerts():
    for alert_id, message in get_pending_alerts("INDIA"):
        print(f"Delivering queued alert #{alert_id}")
        send_telegram_alert(message)
        mark_alert_sent(alert_id)


def main():
    try:
        load_credentials()

        prices = fetch_hyderabad_gold_price()

        city = prices["city"]
        price_24k = prices["24k_per_10g"]
        price_22k = prices["22k_per_10g"]

        # GoodReturns data is currently treated as a daily market price.
        source_date = prices["source_date"]

        print(f"City: {city}")
        print(f"24K: ₹{price_24k:,.0f} per 10g")
        print(f"22K: ₹{price_22k:,.0f} per 10g")
        print(f"Source date: {source_date}")

        previous, inserted = save_india_reading(
            city=city,
            price_24k=price_24k,
            price_22k=price_22k,
            source_date=source_date,
        )

        if not inserted:
            print("India reading already recorded.")
        elif previous is None:
            print("First India reading saved. Baseline established.")
        else:
            print(
                "Previous India prices: "
                f"24K ₹{previous[0]:,.0f}, "
                f"22K ₹{previous[1]:,.0f}"
            )

        deliver_pending_alerts()

    except Exception as error:
        print(f"India gold price check failed: {error}")
        raise


if __name__ == "__main__":
    main()
