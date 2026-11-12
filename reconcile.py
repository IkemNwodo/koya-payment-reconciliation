#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json

def parse_amount(val):
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        return float(val.replace(",", "").strip())
    return float(val)

# Group valid events by txn_id and keep the latest attempt by timestamp
latest_attempts = {}

with open("payments.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except Exception:
            # Ignore lines that can't be read
            continue

        if not isinstance(event, dict) or not event.get("txn_id"):
            # Ignore events without a txn_id
            continue

        txn_id = event["txn_id"]
        ts = event.get("ts", "")

        # Only the latest attempt for each txn_id counts
        if txn_id not in latest_attempts or ts > latest_attempts[txn_id].get("ts", ""):
            latest_attempts[txn_id] = event

total = 0.0
count = 0

for event in latest_attempts.values():
    if event.get("status") == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt", "r", encoding="utf-8") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
