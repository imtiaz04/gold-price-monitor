import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DB_PATH = Path(__file__).resolve().parent / "gold_prices.db"


def initialize_tables(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY,
            price REAL NOT NULL,
            source_updated_at TEXT NOT NULL UNIQUE,
            checked_at TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS pending_alerts (
            id INTEGER PRIMARY KEY,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            sent_at TEXT
        )
    """)


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

        checked_at = datetime.now(ZoneInfo("UTC")).isoformat()

        connection.execute("""
            INSERT INTO readings (
                price, source_updated_at, checked_at
            ) VALUES (?, ?, ?)
        """, (price, source_time, checked_at))

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
                    INSERT INTO pending_alerts (message, created_at)
                    VALUES (?, ?)
                """, (message, checked_at))

        return previous, True


def get_pending_alerts():
    with sqlite3.connect(DB_PATH) as connection:
        initialize_tables(connection)

        return connection.execute("""
            SELECT id, message
            FROM pending_alerts
            WHERE sent_at IS NULL
            ORDER BY id
        """).fetchall()


def mark_alert_sent(alert_id):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            UPDATE pending_alerts
            SET sent_at = ?
            WHERE id = ?
        """, (
            datetime.now(ZoneInfo("UTC")).isoformat(),
            alert_id,
        ))