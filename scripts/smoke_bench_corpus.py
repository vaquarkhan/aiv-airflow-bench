#!/usr/bin/env python3
"""Score a few stored patches from this repo with the local aiv-cli 2.0 jar."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path

BENCH = Path(__file__).resolve().parents[1]
GATE = Path(os.environ["AIV_GATE"]) if os.environ.get("AIV_GATE") else None
E2E = (GATE / "benchmarks" / "industry-e2e" / "run_industry_e2e.py") if GATE else None
JAR = Path(os.environ["AIV_JAR"]) if os.environ.get("AIV_JAR") else (
    (GATE / "aiv-cli" / "target" / "aiv-cli-2.0.jar") if GATE else None
)

CASES = [
    ("e2e-proof", "apache/airflow", 59957, "BLOCK"),
    ("e2e-proof", "apache/airflow", 58593, "PASS"),
    ("e2e-proof", "apache/airflow", 59943, "BLOCK"),
]


def load_e2e():
    spec = importlib.util.spec_from_file_location("e2e", E2E)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # Use this repo's .aiv policy for the smoke.
    mod.POLICY = BENCH / ".aiv"
    mod.JAR = JAR
    return mod


def main():
    if GATE is None or JAR is None or E2E is None:
        raise SystemExit("Set AIV_GATE to the aiv-integrity-gate checkout (and optional AIV_JAR).")
    if not JAR.is_file():
        raise SystemExit(f"missing {JAR}")
    if not E2E.is_file():
        raise SystemExit(f"missing {E2E}")
    e2e = load_e2e()
    token = subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    fetch = e2e.Fetcher(token)
    ok = True
    for folder, repo, number, expect in CASES:
        prs = BENCH / "corpus" / folder / "prs"
        case = {
            "id": f"{folder}-{number}",
            "pr": number,
            "url": f"https://github.com/{repo}/pull/{number}",
            "label": "smoke",
            "kind": "pull_request",
        }
        row = e2e.score_case(repo, case, prs, fetch, JAR)
        print(json.dumps({"id": row["id"], "verdict": row["verdict"], "expect": expect, "rules": row.get("blocking_rules"), "reason": row.get("reason")}), flush=True)
        if row["verdict"] != expect:
            ok = False
        if fetch.stopped:
            print("stopped:", fetch.stopped)
            break
    print("SMOKE", "OK" if ok else "FAIL")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
