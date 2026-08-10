#!/usr/bin/env python3
"""Render a standalone earnings calendar page from the viaNexus API.

    export VIANEXUS_TOKEN=sk_...
    python3 scripts/build.py                  # snapshot page -> calendar.html
    python3 scripts/build.py --no-data        # live page, no data embedded

Reads each symbol in assets/symbols.txt, takes its next expected report, and
inlines the result into assets/template.html. Output is a single file with no
external dependencies, so it can be opened from disk or served from anywhere.

Two shapes come out of the same template:

  snapshot  Data is embedded. Renders instantly, offline, no token needed to
            view. This is what you want for a page you hand to someone.
  live      No data embedded. The page shows a token bar and fetches from
            api.blueskyapi.com itself. This is what you publish, because it
            ships no data of yours.

The token is used only at build time and is never written into either page.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path

import httpx

API = "https://api.blueskyapi.com/v1"
DATASET = "CORE/EARNINGS_CALENDAR"
WORKERS = 8

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def fail(msg):
    sys.exit(f"build.py: {msg}")


def read_symbols(path):
    f = Path(path)
    if not f.exists():
        fail(f"{f} not found")
    symbols = sorted({
        line.strip().upper()
        for line in f.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    })
    if not symbols:
        fail(f"{f} is empty")
    return symbols


def get_record(token, symbol):
    """Next expected report for one symbol, or None.

    A bare GET returns the highest-dated point, which for a forward-looking
    calendar is the next expected report. That is exactly what we want.
    """
    try:
        r = httpx.get(f"{API}/data/{DATASET}/{symbol}", params={"token": token}, timeout=30)
        if r.status_code != 200:
            return None
        body = r.json()
        rows = [body] if isinstance(body, dict) else (body or [])
        if not rows or not rows[0].get("earningsDate"):
            return None
        return {
            "symbol": symbol,
            "date": rows[0]["earningsDate"],
            "session": rows[0].get("marketSession"),
        }
    except httpx.HTTPError:
        return None


def collect(token, symbols):
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        return [r for r in pool.map(lambda s: get_record(token, s), symbols) if r]


def group_by_date(records, today):
    grouped = defaultdict(list)
    for rec in records:
        if rec["date"] >= today:
            grouped[rec["date"]].append([rec["symbol"], rec["session"]])
    for rows in grouped.values():
        rows.sort(key=lambda r: r[0])
    return dict(sorted(grouped.items()))


def render(payload, symbols, generated):
    template = (ASSETS / "template.html").read_text()
    css = (ASSETS / "_shared.css").read_text()

    fields = {
        "__CSS__": css,
        "__DATA__": json.dumps(payload, separators=(",", ":")),
        "__SYMBOLS__": json.dumps(symbols, separators=(",", ":")),
        "__GENERATED__": generated,
    }
    for token, value in fields.items():
        template = template.replace(token, value)

    leftover = re.findall(r"__[A-Z_]+__", template)
    if leftover:
        fail(f"unreplaced placeholders: {sorted(set(leftover))}")

    # The template mentions "pk_" as placeholder text, so match the shape of a
    # real key rather than the bare prefix. Also catch proxystream tickets,
    # which ride along inside predictionSources if that field is ever included.
    leaked = re.findall(r"\b[ps]k_[0-9a-f]{16,}\b|access=[A-Za-z0-9_-]{16,}", template)
    if leaked:
        fail(f"refusing to write output containing {len(leaked)} credential(s)")

    return template


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="calendar.html")
    ap.add_argument("--symbols", default=str(ASSETS / "symbols.txt"))
    ap.add_argument("--token", default=os.environ.get("VIANEXUS_TOKEN"))
    ap.add_argument("--no-data", action="store_true",
                    help="build the live page: no data embedded, token bar shown")
    args = ap.parse_args()

    symbols = read_symbols(args.symbols)
    print(f"{len(symbols)} symbols from {args.symbols}", flush=True)

    if args.no_data:
        payload = {}
        generated = "not loaded"
        print("building live page, no data embedded", flush=True)
    else:
        if not args.token:
            fail("set VIANEXUS_TOKEN, pass --token, or use --no-data")
        today = str(date.today())
        print("fetching calendar...", flush=True)
        records = collect(args.token, symbols)
        missing = len(symbols) - len(records)
        print(f"  {len(records)} records" +
              (f", {missing} symbols returned nothing" if missing else ""), flush=True)
        payload = group_by_date(records, today)
        stranded = len(records) - sum(len(v) for v in payload.values())
        if stranded:
            print(f"  note: {stranded} records are dated in the past and were left out", flush=True)
        generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    Path(args.out).write_text(render(payload, symbols, generated))
    print(f"wrote {args.out}", flush=True)


if __name__ == "__main__":
    main()
