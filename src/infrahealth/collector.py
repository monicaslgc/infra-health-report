"""Where inventory data comes from.

`load_from_json` reads a static file, which is what the demo uses so the
whole thing runs offline with no credentials. In a real setup you'd write a
second loader against whatever hypervisor/monitoring API you have (Proxmox,
Prometheus, whatever) and return the same list[Resource] -- the analyzer
doesn't know or care where the data came from.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .models import MetricSample, Resource, ResourceKind


def load_from_json(path: Path) -> list[Resource]:
    data = json.loads(path.read_text(encoding="utf-8"))
    resources = []
    for item in data["resources"]:
        history = [
            MetricSample(
                sample_date=date.fromisoformat(h["date"]),
                cpu_percent=h["cpu_percent"],
                mem_percent=h["mem_percent"],
                disk_percent=h["disk_percent"],
            )
            for h in item["history"]
        ]
        history.sort(key=lambda s: s.sample_date)
        resources.append(
            Resource(
                id=item["id"],
                name=item["name"],
                kind=ResourceKind(item["kind"]),
                node=item["node"],
                history=history,
            )
        )
    return resources
