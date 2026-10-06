# Gold Price Monitoring & Alerting System

A Python-based multi-market gold price monitoring and alerting system that tracks gold prices for the **USA and India**, stores historical price data, detects price movements, and sends automated notifications through **Telegram**.

The project demonstrates practical concepts around Python automation, monitoring, persistence, alert processing, scheduling, and secure credential management.

---

## Features

- Monitors USA gold prices in **USD per troy ounce**
- Monitors India gold prices in **INR per 10 grams**
- Stores historical price readings using **SQLite**
- Compares the current price with the previous reading
- Calculates absolute and percentage price changes
- Detects both upward and downward price movements
- Maintains separate **USA and India alert queues**
- Sends automated alerts through Telegram
- Supports Linux shell-script execution
- Supports scheduled execution through GitHub Actions
- Keeps Telegram credentials outside the source code

---

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

The USA and India monitoring paths are handled independently while using the same overall monitoring architecture.

Separate alert queues provide isolation between the two markets and make the notification workflow easier to troubleshoot and extend.

---

# Getting Started

The following steps explain how to run the project locally after cloning or forking the repository.

## 1. Clone the Repository

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd gold-price-monitor
```

If you forked the project first, clone your fork instead.

---

## 2. Create a Python Virtual Environment

Create the environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Your terminal should now show something similar to:

```text
(.venv) user@machine:~/gold-price-monitor$
```

---

## 3. Dependencies

This project currently uses only Python standard-library modules, so no third-party Python packages need to be installed.

The main modules used include:

```text
datetime
pathlib
urllib
zoneinfo
html
json
os
re
sqlite3
sys
```

The remaining imports are local modules included in this repository:

```text
database
india_price
notifications
price_api
```

Therefore, after creating and activating the virtual environment, you can run the project without installing additional pip packages.

You can verify your Python version with:

```bash
python3 --version
```
---

## 4. Create Your Own Telegram Bot

This project does **not** provide Telegram credentials.

Each user should create and use their own Telegram bot.

Using Telegram's BotFather:

1. Create a new bot
2. Obtain the bot token
3. Obtain the Telegram chat ID where alerts should be delivered

You will need:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Never add these values directly to the Python source code.

---

## 5. Configure Telegram Credentials

Set the credentials as environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your-own-bot-token"
export TELEGRAM_CHAT_ID="your-own-chat-id"
```

You can verify that the chat ID is available:

```bash
echo "$TELEGRAM_CHAT_ID"
```

Avoid printing the bot token to the terminal unnecessarily.

---

## 6. Run the USA Gold Monitor

Run:

```bash
python3 gold_monitor.py
```

The USA monitor:

```text
Fetch USA Gold Price
        |
        v
Normalize Price
        |
        v
Store Reading in SQLite
        |
        v
Read Previous Price
        |
        v
Calculate Price Change
        |
        v
USA Alert Queue
        |
        v
Telegram Notification
```

Example output:

```text
Gold price: $4,177.40 USD per troy ounce
Previous price: $4,173.20
Change since previous reading: $+4.20 (+0.101%)
Delivering queued alert
Telegram alert sent.
```

---

## 7. Run the India Gold Monitor

Run:

```bash
python3 india_monitor.py
```

The India monitor follows a separate monitoring path:

```text
Fetch India Gold Price
        |
        v
Normalize INR Price
        |
        v
Store Reading in SQLite
        |
        v
Read Previous India Price
        |
        v
Calculate Price Change
        |
        v
India Alert Queue
        |
        v
Telegram Notification
```

This separation prevents the USA and India alert workflows from interfering with each other.

---

## 8. Local SQLite Database

The application maintains its own local SQLite database:

```text
gold_prices.db
```

The database stores historical readings used for price comparison and alert processing.

The database is intentionally excluded from Git using `.gitignore`.

This means every person who clones the repository creates and maintains their **own local monitoring history**.

---

## 9. Run Using Shell Scripts

The project includes shell scripts for running the monitors.

USA:

```bash
./run_monitor.sh
```

India:

```bash
./run_india_monitor.sh
```

If the scripts are not executable:

```bash
chmod +x run_monitor.sh run_india_monitor.sh
```

Then run them again.

---

## 10. GitHub Actions

The repository includes a GitHub Actions workflow:

```text
.github/workflows/gold-monitor.yml
```

If you fork the repository and want to run the workflow from your own GitHub account, configure your own repository secrets.

Add:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

under:

```text
Repository
    |
    v
Settings
    |
    v
Secrets and variables
    |
    v
Actions
    |
    v
Repository secrets
```

The original repository's secrets are **not transferred** when another user forks or clones the repository.

---

## Processing Flow

Each monitoring cycle follows the same general pattern:

```text
Price Source
     |
     v
Fetch Price
     |
     v
Normalize Data
     |
     v
SQLite Price History
     |
     v
Current vs Previous
     |
     v
Calculate Change
     |
     v
Alert Queue
     |
     v
Telegram
```

---

## Example Alerts

### Price Increase

```text
Gold alert: UP

Current: $4,177.40 USD per troy ounce
Previous: $4,173.20
Change: +4.20 USD (+0.101%)
```

### Price Decrease

```text
Gold alert: DOWN

Current: $4,173.60 USD per troy ounce
Previous: $4,177.40
Change: -3.80 USD (-0.091%)
```

The monitor therefore handles both upward and downward price movements.

---

## Project Structure

```text
gold-price-monitor/
│
├── .github/
│   └── workflows/
│       └── gold-monitor.yml
│
├── database.py
├── gold_monitor.py
├── india_monitor.py
├── india_price.py
├── notifications.py
├── price_api.py
├── run_monitor.sh
├── run_india_monitor.sh
├── .gitignore
└── README.md
```

Runtime files such as databases and logs are intentionally excluded from the repository.

---

## Security

Credentials are not hardcoded into the application.

For local execution, the application retrieves credentials at runtime using environment variables such as:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

GitHub Actions retrieves the corresponding values using GitHub repository secrets.

The repository `.gitignore` excludes common sensitive and runtime files including:

```text
.env
.env.*
*.db
*.sqlite
*.sqlite3
*.log
*.lock
.venv/
__pycache__/
```

### Never commit

- Telegram bot tokens
- Telegram chat IDs
- API keys
- Passwords
- `.env` files
- Local databases
- Application logs

---

## Tech Stack

- Python
- SQLite
- Telegram Bot API
- Linux
- Bash
- Git
- GitHub
- GitHub Actions

---

## Design Decisions

### Separate USA and India Alert Queues

USA and India alerts are processed independently.

This provides better isolation and makes it easier to troubleshoot or extend one market without affecting the other.

### SQLite for Persistence

SQLite keeps the project lightweight while still providing persistent historical state for price comparisons and alert processing.

For a larger production system, this could be replaced with a managed relational or time-series database.

### Externalized Credentials

Secrets are kept outside the source code.

Local execution uses runtime credentials, while GitHub Actions uses repository secrets.

This prevents credentials from being exposed when the repository is shared or forked.

---

## Future Improvements

Possible next steps include:

- Dockerize the monitoring services
- Add retry and exponential backoff
- Add stronger alert deduplication and idempotency
- Add Prometheus metrics
- Build Grafana dashboards
- Add centralized logging
- Add monitor health checks
- Improve failure/recovery handling
- Deploy the monitoring system to AWS
- Replace SQLite with a managed database if scale requires it

---

## What I Learned

This project reinforced that monitoring is more than periodically fetching data.

A useful monitoring system also needs to consider:

- Historical state
- Data normalization
- Change detection
- Persistent storage
- Alert conditions
- Notification delivery
- Failure handling
- Security
- Scheduling
- Isolation between independent workflows

The project started as a simple gold-price automation idea and evolved into a small multi-market monitoring and alerting system.