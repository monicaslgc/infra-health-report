import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from infrahealth.collector import load_from_json
from infrahealth.models import ResourceKind


def test_load_from_json_reads_the_sample_cluster():
    path = Path(__file__).resolve().parent.parent / "examples" / "cluster.json"

    resources = load_from_json(path)

    assert len(resources) == 6
    reporting_db = next(r for r in resources if r.id == "vm-101")
    assert reporting_db.name == "reporting-db"
    assert reporting_db.kind == ResourceKind.VM
    assert len(reporting_db.history) == 2
    # sorted chronologically, so the latest sample is last
    assert reporting_db.history[-1].sample_date > reporting_db.history[0].sample_date
