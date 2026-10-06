#!/bin/bash
set -eu
umask 077

cd /home/imtiaz/Documents/gold-price-monitor

exec /usr/bin/flock -n .india-monitor.lock \
    .venv/bin/python -u india_monitor.py
