#!/usr/bin/env python3
"""Run a capacity report over the sample cluster.

Usage:
    python examples/run_report.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from infrahealth import analyze  # noqa: E402
from infrahealth.collector import load_from_json  # noqa: E402


def main() -> None:
    inventory_path = Path(__file__).resolve().parent / "cluster.json"
    resources = load_from_json(inventory_path)

    report = analyze(resources, source_label=str(inventory_path.name))
    print(report)


if __name__ == "__main__":
    main()
