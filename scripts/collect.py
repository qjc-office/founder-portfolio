#!/usr/bin/env python3
"""Stub collector for founder-portfolio.

The full implementation will enrich profile.yaml from
~/qjc-office/customer-index.json (clients of record, project recency, etc.).
For now this just confirms the contract and exits cleanly.

Usage:
    collect.py --enrich-from-customer-index
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Enrich profile.yaml from customer-index (stub).")
    p.add_argument(
        "--enrich-from-customer-index",
        action="store_true",
        help="Pull clients from ~/qjc-office/customer-index.json (not yet implemented).",
    )
    p.parse_args(argv)
    print(
        "TODO: enrichment from ~/qjc-office/customer-index.json not yet implemented; "
        "use static profile.yaml"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
