import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from infrahealth import analyze
from infrahealth.models import MetricSample, Resource, ResourceKind, Severity, Metric


def make_resource(cpu_hist, mem_hist=None, disk_hist=None, **overrides):
    """Build a two-sample resource. cpu_hist/mem_hist/disk_hist are (start, end) pairs."""
    mem_hist = mem_hist or (30.0, 30.0)
    disk_hist = disk_hist or (30.0, 30.0)
    defaults = dict(id="r1", name="test-resource", kind=ResourceKind.VM, node="node-x")
    defaults.update(overrides)
    return Resource(
        history=[
            MetricSample(date(2026, 8, 15), cpu_hist[0], mem_hist[0], disk_hist[0]),
            MetricSample(date(2026, 9, 14), cpu_hist[1], mem_hist[1], disk_hist[1]),
        ],
        **defaults,
    )


def test_resource_over_critical_threshold_is_flagged_critical():
    resource = make_resource(cpu_hist=(50.0, 95.0))

    report = analyze([resource])

    cpu_findings = [f for f in report.findings if f.metric == Metric.CPU]
    assert len(cpu_findings) == 1
    assert cpu_findings[0].severity == Severity.CRITICAL


def test_resource_within_thresholds_and_flat_is_not_flagged():
    resource = make_resource(cpu_hist=(20.0, 21.0), mem_hist=(20.0, 21.0), disk_hist=(20.0, 21.0))

    report = analyze([resource])

    assert report.findings == []


def test_ok_resource_trending_upward_gets_a_days_to_critical_projection():
    # disk goes from 70 to 88 over 30 days -> climbing fast enough to flag
    resource = make_resource(cpu_hist=(10.0, 10.0), mem_hist=(10.0, 10.0), disk_hist=(70.0, 88.0))

    report = analyze([resource])

    disk_findings = [f for f in report.findings if f.metric == Metric.DISK]
    assert len(disk_findings) == 1
    assert disk_findings[0].days_to_critical is not None
    assert disk_findings[0].days_to_critical > 0


def test_declining_trend_never_projects_days_to_critical():
    resource = make_resource(cpu_hist=(60.0, 40.0))  # trending down, still under warning

    report = analyze([resource])

    assert report.findings == []


def test_report_str_lists_critical_before_warning():
    critical_resource = make_resource(id="r-critical", cpu_hist=(90.0, 96.0))
    warning_resource = make_resource(id="r-warning", cpu_hist=(50.0, 75.0))

    report = analyze([warning_resource, critical_resource])
    text = str(report)

    assert text.index("CRITICAL") < text.index("WARNING")
