"""Turns resource history into a Report.

Two things happen per resource/metric: check the current value against
threshold, and if there's more than one history point, work out a rough
daily trend so a resource that's still under threshold today but climbing
fast still shows up with a days-to-critical estimate. This is deliberately
a straight-line projection, not a real forecasting model -- good enough to
turn "check again next week" into "this one needs attention this week."
"""

from __future__ import annotations

from typing import Optional

from .models import Finding, Metric, Report, Resource, Severity
from .thresholds import DEFAULT_THRESHOLDS, Threshold


def _severity(value: float, threshold: Threshold) -> Severity:
    if value >= threshold.critical:
        return Severity.CRITICAL
    if value >= threshold.warning:
        return Severity.WARNING
    return Severity.OK


def _trend_per_day(resource: Resource, metric: Metric) -> float:
    if len(resource.history) < 2:
        return 0.0
    first, last = resource.earliest, resource.latest
    days = (last.sample_date - first.sample_date).days
    if days <= 0:
        return 0.0
    return (last.value_for(metric) - first.value_for(metric)) / days


def _days_to_critical(current: float, trend_per_day: float, threshold: Threshold) -> Optional[int]:
    if trend_per_day <= 0 or current >= threshold.critical:
        return None
    days = (threshold.critical - current) / trend_per_day
    return max(0, round(days))


def analyze(
    resources: list[Resource],
    thresholds: dict[Metric, Threshold] = DEFAULT_THRESHOLDS,
    source_label: str = "inventory",
) -> Report:
    findings: list[Finding] = []

    for resource in resources:
        current = resource.latest
        for metric in Metric:
            threshold = thresholds[metric]
            value = current.value_for(metric)
            severity = _severity(value, threshold)
            trend = _trend_per_day(resource, metric)

            # Flag it if it's already over threshold, or trending toward
            # critical within a reasonable horizon even while still OK/warning.
            days_out = _days_to_critical(value, trend, threshold) if trend > 0 else None
            worth_flagging = severity != Severity.OK or (days_out is not None and days_out <= 30)
            if not worth_flagging:
                continue

            findings.append(
                Finding(
                    resource_id=resource.id,
                    resource_name=resource.name,
                    node=resource.node,
                    metric=metric,
                    current_value=value,
                    severity=severity,
                    warning_threshold=threshold.warning,
                    critical_threshold=threshold.critical,
                    trend_per_day=trend,
                    days_to_critical=days_out,
                )
            )

    return Report(generated_from=source_label, findings=findings)
