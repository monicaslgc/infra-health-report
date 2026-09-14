"""Core data types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class ResourceKind(str, Enum):
    VM = "vm"
    CONTAINER = "container"


class Metric(str, Enum):
    CPU = "cpu_percent"
    MEMORY = "mem_percent"
    DISK = "disk_percent"


class Severity(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class MetricSample:
    """One point-in-time reading for a resource."""

    sample_date: date
    cpu_percent: float
    mem_percent: float
    disk_percent: float

    def value_for(self, metric: Metric) -> float:
        return {
            Metric.CPU: self.cpu_percent,
            Metric.MEMORY: self.mem_percent,
            Metric.DISK: self.disk_percent,
        }[metric]


@dataclass
class Resource:
    """A VM or container tracked on a node, with its metric history."""

    id: str
    name: str
    kind: ResourceKind
    node: str
    history: list[MetricSample] = field(default_factory=list)

    @property
    def latest(self) -> MetricSample:
        return self.history[-1]

    @property
    def earliest(self) -> MetricSample:
        return self.history[0]


@dataclass
class Finding:
    """One thing the analyzer flagged: a resource/metric over (or approaching) threshold."""

    resource_id: str
    resource_name: str
    node: str
    metric: Metric
    current_value: float
    severity: Severity
    warning_threshold: float
    critical_threshold: float
    trend_per_day: float = 0.0
    days_to_critical: Optional[int] = None

    def __str__(self) -> str:  # pragma: no cover - formatting only
        line = (
            f"[{self.severity.value.upper():8s}] {self.node}/{self.resource_name} "
            f"{self.metric.value}={self.current_value:.1f}%"
        )
        if self.days_to_critical is not None:
            line += f" -> projected to hit {self.critical_threshold:.0f}% in ~{self.days_to_critical}d"
        return line


@dataclass
class Report:
    generated_from: str
    findings: list[Finding] = field(default_factory=list)

    def by_severity(self, severity: Severity) -> list[Finding]:
        return [f for f in self.findings if f.severity == severity]

    def __str__(self) -> str:  # pragma: no cover - formatting only
        critical = self.by_severity(Severity.CRITICAL)
        warning = self.by_severity(Severity.WARNING)
        trending = [f for f in self.by_severity(Severity.OK) if f.days_to_critical is not None]

        lines = [f"Capacity report ({self.generated_from})"]
        lines.append(f"  {len(critical)} critical, {len(warning)} warning, {len(trending)} trending toward critical")

        severity_order = {Severity.CRITICAL: 0, Severity.WARNING: 1, Severity.OK: 2}
        ordered = sorted(self.findings, key=lambda f: (severity_order[f.severity], -f.current_value))
        for f in ordered:
            lines.append(f"  {f}")
        if not self.findings:
            lines.append("  everything within thresholds")
        return "\n".join(lines)
