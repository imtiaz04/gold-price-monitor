import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


DB_PATH = Path(__file__).resolve().parent / "gold_prices.db"


def initialize_tables(connection):
    # USA MARKET TABLE - XAU/USD spot gold
    connection.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY,
            price REAL NOT NULL,
            source_updated_at TEXT NOT NULL UNIQUE,
            checked_at TEXT NOT NULL
        )
    """)

    # TELEGRAM ALERT QUEUE - market-specific USA/India alerts
    connection.execute("""
        CREATE TABLE IF NOT EXISTS pending_alerts (
            id INTEGER PRIMARY KEY,
            market TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            sent_at TEXT
        )
    """)

    # Migrate an existing database that does not yet have a market column.
    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(pending_alerts)"
        )
    }

    if "market" not in columns:
        connection.execute(
            "ALTER TABLE pending_alerts ADD COLUMN market TEXT"
        )

        # Classify existing alerts so old history is preserved.
        connection.execute("""
            UPDATE pending_alerts
            SET market = CASE
                WHEN message LIKE '%Hyderabad%' THEN 'INDIA'
                ELSE 'USA'
            END
            WHERE market IS NULL
        """)

    # INDIA MARKET TABLE - Hyderabad 24K and 22K gold in INR
    connection.execute("""
        CREATE TABLE IF NOT EXISTS india_readings (
            id INTEGER PRIMARY KEY,
            city TEXT NOT NULL,
            price_24k REAL NOT NULL,
            price_22k REAL NOT NULL,
            source_date TEXT NOT NULL,
            checked_at TEXT NOT NULL
        )
    """)


# USA MARKET - save XAU/USD reading and queue price-change alert
def save_reading(price, updated_at, threshold):
    with sqlite3.connect(DB_PATH) as connection:
        initialize_tables(connection)
        connection.execute("BEGIN IMMEDIATE")

        previous = connection.execute("""
            SELECT price, source_updated_at
            FROM readings
            ORDER BY source_updated_at DESC
            LIMIT 1
        """).fetchone()

        source_time = updated_at.astimezone(
            ZoneInfo("UTC")
        ).isoformat()

        if previous and source_time <= previous[1]:
            return previous, False

        checked_at = datetime.now(
            ZoneInfo("UTC")
        ).isoformat()

        connection.execute("""
            INSERT INTO readings (
                price,
                source_updated_at,
                checked_at
            ) VALUES (?, ?, ?)
        """, (
            price,
            source_time,
            checked_at,
        ))

        if previous:
            change = price - previous[0]

            if change != 0:
                direction = "UP" if change > 0 else "DOWN"
                percentage = (change / previous[0]) * 100

                local_time = updated_at.astimezone(
                    ZoneInfo("America/New_York")
                )

                message = (
                    f"Gold alert: {direction}\n"
                    f"Current: ${price:,.2f} USD per troy ounce\n"
                    f"Previous: ${previous[0]:,.2f}\n"
                    f"Change: {change:+,.2f} USD "
                    f"({percentage:+.3f}%)\n"
                    f"Source updated: "
                    f"{local_time:%Y-%m-%d %I:%M:%S %p %Z}"
                )

                connection.execute("""
                    INSERT INTO pending_alerts (
                        market,
                        message,
                        created_at
                    ) VALUES (?, ?, ?)
                """, (
                    "USA",
                    message,
                    checked_at,
                ))

        return previous, True


# INDIA MARKET - save Hyderabad 24K/22K reading
# and queue price-change alert
def save_india_reading(
    city,
    price_24k,
    price_22k,
    source_date,
):
    with sqlite3.connect(DB_PATH) as connection:
        initialize_tables(connection)
        connection.execute("BEGIN IMMEDIATE")

        previous = connection.execute("""
            SELECT
                price_24k,
                price_22k,
                source_date
            FROM india_readings
            WHERE city = ?
            ORDER BY id DESC
            LIMIT 1
        """, (city,)).fetchone()

        checked_at = datetime.now(
            ZoneInfo("UTC")
        ).isoformat()

        # Do not insert the same market date and prices repeatedly.
        if (
            previous
            and previous[2] == source_date
            and previous[0] == price_24k
            and previous[1] == price_22k
        ):
            return previous, False

        connection.execute("""
            INSERT INTO india_readings (
                city,
                price_24k,
                price_22k,
                source_date,
                checked_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            city,
            price_24k,
            price_22k,
            source_date,
            checked_at,
        ))

        if previous:
            change_24k = price_24k - previous[0]
            change_22k = price_22k - previous[1]

            if change_24k != 0 or change_22k != 0:
                percentage_24k = (
                    change_24k / previous[0]
                ) * 100

                percentage_22k = (
                    change_22k / previous[1]
                ) * 100

                message = (
                    f"🇮🇳 Hyderabad Gold Alert\n\n"
                    f"24K / 10g\n"
                    f"Previous: ₹{previous[0]:,.0f}\n"
                    f"Current: ₹{price_24k:,.0f}\n"
                    f"Change: "
                    f"{'+' if change_24k > 0 else '-'}"
                    f"₹{abs(change_24k):,.0f} "
                    f"({percentage_24k:+.3f}%)\n\n"
                    f"22K / 10g\n"
                    f"Previous: ₹{previous[1]:,.0f}\n"
                    f"Current: ₹{price_22k:,.0f}\n"
                    f"Change: "
                    f"{'+' if change_22k > 0 else '-'}"
                    f"₹{abs(change_22k):,.0f} "
                    f"({percentage_22k:+.3f}%)\n\n"
                    f"Market: {city}\n"
                    f"Market date: {source_date}"
                )

                connection.execute("""
                    INSERT INTO pending_alerts (
                        market,
                        message,
                        created_at
                    ) VALUES (?, ?, ?)
                """, (
                    "INDIA",
                    message,
                    checked_at,
                ))

        return previous, True


# MARKET-SPECIFIC ALERT QUEUE
# Retrieve only unsent alerts belonging to the requested market.
def get_pending_alerts(market):
    with sqlite3.connect(DB_PATH) as connection:
        initialize_tables(connection)

        return connection.execute("""
            SELECT id, message
            FROM pending_alerts
            WHERE sent_at IS NULL
              AND market = ?
            ORDER BY id
        """, (market,)).fetchall()


# SHARED ALERT QUEUE
# Mark a Telegram alert as successfully delivered.
def mark_alert_sent(alert_id):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            UPDATE pending_alerts
            SET sent_at = ?
            WHERE id = ?
        """, (
            datetime.now(
                ZoneInfo("UTC")
            ).isoformat(),
            alert_id,
        ))