"""Look up every dev-list subject from the inbox screenshots."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

SUBJECTS = [
    'Merging "almost" ready PRs with maintainer-fixups',
    "Airflow Contributor Day in Glasgow",
    "hardened, trixie-based PROD images",
    "Human Summary section in agent-drafted PR descriptions",
    "Python 3.10 dropped",
    "Limiting number of opened pull requests",
    "llms.txt and Markdown docs for coding agents",
    "AIP-104 Iterable Tasks",
    "[secrets]backend_order",
    "asf incubator logo",
    "MLH Fellowship on Airflow",
    "release preparation date 2026-10-02",
    "Maggie's onboarding skill",
    "Preparing for Airflow 3.4.0 Release",
    "A release candidate checker",
    "Separate dag bundle discovery and import roots",
    "Release Airflow 3.3.2 from 3.3.2rc1",
    "release preparation date 2026-10-14",
    "Maggie Meetup 2026 in Seoul",
    "Providers packages prepared on 2026-10-17",
    "Native asset-event emission from tasks",
    "Enable auto-merge for PRs to main",
    "release preparation date 2026-10-17",
    "AIP-120 Run CI for external contributions",
    "Providers packages prepared on 2026-10-14",
    "scheduled triaging and security issues",
    "release preparation date 2026-10-06",
    "AIP-118: Self-hosted runners",
    "Newsfragments: when to add one",
    "Requiring real GCP testing evidence",
    'your PR, your CI',
    "Apache Trusted Releases platform",
    "Providers packages prepared on 2026-10-06",
    "Dropping Python 3.10 support",
    "September 2026 PR of the Month",
    "AIP-109 DAG Version Picking",
    "September 2026 Version Rookie",
    "Airflow Open Spaces at PyCon TW",
    "Deprecate cyclic TaskGroup dependencies",
    "pull request limit is temporarily a soft limit",
    "Contributor Day at Community Over Code Glasgow",
    "Anomaly monitoring and guardrails for the Airflow AWS",
    "Microsoft Fabric Provider",
]

OUT = Path(__file__).resolve().parent / "ai-year" / "inbox-check.json"


def get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "aiv-bench-corpus"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search(q: str) -> dict:
    url = "https://lists.apache.org/api/stream.json?" + urllib.parse.urlencode({
        "list": "dev",
        "domain": "airflow.apache.org",
        "social": "yes",
        "header_subject": q,
        "quant": "3",
        "page": "0",
        "d": "2026",
    })
    data = get(url)
    rows = data.get("rows") or []
    if rows:
        return data
    url = "https://lists.apache.org/api/stream.json?" + urllib.parse.urlencode({
        "list": "dev",
        "domain": "airflow.apache.org",
        "social": "yes",
        "q": q,
        "quant": "3",
        "page": "0",
    })
    return get(url)


def main() -> None:
    found = []
    for q in SUBJECTS:
        data = search(q)
        rows = data.get("rows") or []
        print(f"{len(rows):2} {q}", flush=True)
        for row in rows[:2]:
            starter = row.get("starter") or {}
            found.append({
                "query": q,
                "tid": row.get("tid"),
                "subject": row.get("subject"),
                "epoch": row.get("epoch"),
                "replies": row.get("replies"),
                "url": f"https://lists.apache.org/thread/{row.get('tid')}",
                "from": (starter.get("from") or ""),
                "excerpt": (starter.get("body") or "")[:900],
            })
    OUT.write_text(json.dumps(found, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", len(found), OUT, flush=True)


if __name__ == "__main__":
    main()
