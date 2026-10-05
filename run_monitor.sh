#!/bin/bash
set -eu
umask 077

cd /home/imtiaz/Documents/gold-price-monitor

exec /usr/bin/flock -n .monitor.lock \
    .venv/bin/python -u gold_monitor.py
