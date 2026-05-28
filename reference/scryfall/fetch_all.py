#!/usr/bin/env python3
"""Fetch every page of a Scryfall search and save as one combined JSON file.

Respects Scryfall's etiquette: User-Agent header, 100ms delay between requests.
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

QUERY = "is:commander"
HEADERS = {
    "User-Agent": "MTGProjectResearch/0.1 (serina.mcfall@gmail.com)",
    "Accept": "application/json",
}
HERE = Path(__file__).parent
OUT = HERE / "commanders-all.raw.json"

start = (
    f"https://api.scryfall.com/cards/search"
    f"?q={urllib.request.quote(QUERY)}&unique=cards&order=name&page=1"
)


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


all_cards: list[dict] = []
url = start
page = 0
total = None
while url:
    page += 1
    payload = fetch(url)
    if total is None:
        total = payload.get("total_cards")
        print(f"Total cards reported: {total:,}")
    chunk = payload.get("data", [])
    all_cards.extend(chunk)
    print(f"  page {page}: +{len(chunk)} (running total {len(all_cards):,})")
    if payload.get("has_more") and payload.get("next_page"):
        url = payload["next_page"]
        time.sleep(0.1)  # Scryfall asks for ≥50–100ms between requests
    else:
        url = None

combined = {
    "object": "list",
    "total_cards": total,
    "has_more": False,
    "data": all_cards,
}
OUT.write_text(json.dumps(combined))
print(f"\nWrote {len(all_cards):,} cards → {OUT} ({OUT.stat().st_size:,} bytes)")
