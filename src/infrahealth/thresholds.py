"""Default warning/critical thresholds per metric.

These are just sane defaults for the demo, not a recommendation for any real
environment. A real deployment would probably make these per-resource
(a database node's disk threshold isn't the same as a stateless worker's).
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import Metric


@dataclass(frozen=True)
class Threshold:
    warning: float
    critical: float


DEFAULT_THRESHOLDS: dict[Metric, Threshold] = {
    Metric.CPU: Threshold(warning=70.0, critical=90.0),
    Metric.MEMORY: Threshold(warning=75.0, critical=90.0),
    Metric.DISK: Threshold(warning=80.0, critical=95.0),
}
