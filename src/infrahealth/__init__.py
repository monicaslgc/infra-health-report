"""infrahealth: turns raw VM/container resource metrics into an actionable capacity report.

Point it at a JSON inventory (see examples/cluster.json) and it flags anything
over threshold, plus projects roughly how many days out a resource that's
trending upward will actually hit that threshold. No external services, no
real infrastructure connection required to run the demo.
"""

from .models import Resource, Finding, Report, Severity
from .analyzer import analyze

__all__ = ["Resource", "Finding", "Report", "Severity", "analyze"]
__version__ = "0.1.0"
