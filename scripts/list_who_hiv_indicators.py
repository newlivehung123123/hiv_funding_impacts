#!/usr/bin/env python3
"""
Dump the WHO GHO HIV indicator catalogue to docs/who_hiv_indicators.csv.

  >>> YOU run this. Use it to review real indicator codes/names and then lock exact
      {canonical: who_code} mappings (pass them to WHOGHOConnector) instead of relying
      on the connector's name-hint auto-resolution.
"""
from __future__ import annotations

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hivimpact.connectors.who_gho import WHOGHOConnector


def main() -> int:
    conn = WHOGHOConnector()
    catalogue = conn.list_hiv_indicators()
    os.makedirs("docs", exist_ok=True)
    out = "docs/who_hiv_indicators.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["IndicatorCode", "IndicatorName"])
        for e in sorted(catalogue, key=lambda x: x.get("IndicatorName", "")):
            w.writerow([e.get("IndicatorCode", ""), e.get("IndicatorName", "")])
    print(f"wrote {len(catalogue)} HIV indicators to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
