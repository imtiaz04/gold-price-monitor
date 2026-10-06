# Gold Price Monitoring & Alerting System

A Python-based multi-market gold price monitoring system that tracks gold prices for the USA and India, stores historical price data, detects price movements, and sends automated alerts through Telegram.

## Features

- Monitors USA gold prices in USD per troy ounce
- Monitors India gold prices in INR per 10 grams
- Stores historical price readings in SQLite
- Compares current prices with previous readings
- Calculates absolute and percentage price changes
- Detects both upward and downward price movements
- Maintains separate USA and India alert queues
- Sends automated Telegram notifications
- Supports scheduled execution on Linux
- Uses local credential storage instead of hardcoding Telegram secrets

## Architecture

```text
                    GOLD PRICE MONITOR
                     /              \
                    /                \
             USA Monitor          India Monitor
             USD / Ounce          INR / 10 Gram
                  |                    |
             Fetch Price          Fetch Price
                  |                    |
           Normalize Data       Normalize Data
                    \              /
                     \            /
                  SQLite Price History
                          |
                 Compare Current Price
                  with Previous Price
                          |
                   Calculate Change
                     /          \
                    /            \
          USA Alert Queue    India Alert Queue
                    \            /
                     \          /
                     Telegram Bot
                          |
                     Price Alert
```

## Processing Flow

Each monitoring cycle follows this workflow:

```text
Fetch Price
    |
    v
Normalize Data
    |
    v
Store / Read SQLite History
    |
    v
Compare Current vs Previous Price
    |
    v
Calculate Price and Percentage Change
    |
    v
Queue Alert
    |
    v
Telegram Notification
```

The USA and India monitoring paths use separate alert queues so that notifications for one market do not interfere with the other.

## Example USA Alert

```text
Gold alert: UP
Current: $4,177.40 USD per troy ounce
Previous: $4,173.20
Change: +4.20 USD (+0.101%)
```

The monitor also detects downward movements:

```text
Gold alert: DOWN
Current: $4,173.60 USD per troy ounce
Previous: $4,177.40
Change: -3.80 USD (-0.091%)
```

## Project Structure

```text
gold-price-monitor/
├── gold_monitor.py
├── india_monitor.py
├── database.py
├── run_india_monitor.sh
├── README.md
└── gold_prices.db
```

## Tech Stack

- Python
- SQLite
- Telegram Bot API
- Linux
- Bash
- Scheduled Jobs
- External gold-price data sources

## Security

Telegram credentials are stored locally and are not hardcoded into the application source code.

Sensitive files and credentials should be excluded from Git using `.gitignore`.

Never commit Telegram bot tokens, API keys, passwords, or other secrets to the repository.

## Future Improvements

- Dockerize the monitoring services
- Add retry and exponential backoff for external API failures
- Add Prometheus application metrics
- Build Grafana dashboards
- Add centralized logging
- Improve alert deduplication and idempotency
- Add health checks for the monitoring processes
- Deploy the monitoring system to AWS

## What I Learned

This project demonstrates that monitoring involves more than periodically fetching data.

A reliable monitoring workflow needs:

- Historical state
- Change detection
- Alert conditions
- Persistent storage
- Notification delivery
- Failure handling
- Separation between independent monitoring workflows
- Logging and troubleshooting

The project helped me apply these concepts in a practical Python automation project.