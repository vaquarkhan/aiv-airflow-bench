"""Publish a 6-month cut and the full-year cut of the corpus.

Local rows are the stored samples. GitHub totals are search total_count
for the same windows, not a census and not a slop count.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import collect_slop_benches as b

ROOT = Path(__file__).resolve().parents[1]
YEAR_START = dt.date(2025, 10, 22)
SIX_START = dt.date(2026, 4, 22)
END = dt.date(2026, 10, 22)

REPOS = [
    ("airflow", "apache/airflow"),
    ("flink", "apache/flink"),
    ("kafka", "apache/kafka"),
    ("curl", "curl/curl"),
    ("godot", "godotengine/godot"),
    ("ghostty", "ghostty-org/ghostty"),
    ("cosmic", "pop-os/cosmic-comp"),
]
EXTRAS = [
    ("pull_requests", "is:pr"),
    ("closed_unmerged", "is:pr is:closed -is:merged"),
    ("generated_by", 'is:pr "Generated-by:"'),
    ("slop_language", '"AI slop" OR "vibe coding" OR "vibe coded" OR "vibe-coded"'),
]
AIRFLOW_TOOLS = ["Claude", "Codex", "Copilot", "Gemini", "ChatGPT"]


def in_window(when: dt.datetime | None, start: dt.date) -> bool:
    if when is None:
        return False
    day = when.date()
    return start <= day <= END


def parse_when(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    text = value.replace("Z", "+00:00")
    try:
        return dt.datetime.fromisoformat(text)
    except ValueError:
        return None


def tally(rows: list[dict], start: dt.date) -> dict:
    classes: Counter[str] = Counter()
    kept = 0
    for row in rows:
        when = parse_when(row.get("created_at"))
        if when is None and row.get("month"):
            # Month buckets are stored as YYYY-MM. The 22nd keeps Oct 2025
            # inside the year window and Apr 2026 inside the six-month window.
            when = parse_when(f"{row['month']}-22T00:00:00+00:00")
        if not in_window(when, start):
            continue
        kept += 1
        label = row.get("label")
        if isinstance(label, dict):
            label = label.get("class")
        classes[label or row.get("class") or "unknown"] += 1
    return {"cases": kept, "by_class": dict(classes)}


def load_cases() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    proof = json.loads((ROOT / "docs" / "data" / "e2e-proof-latest.json").read_text(encoding="utf-8"))
    out["airflow"] = proof["cases"]
    for name, _repo in REPOS:
        if name == "airflow":
            continue
        path = ROOT / "corpus" / "benchmarks" / name / "cases.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        out[name] = doc["cases"]
    return out


def count_jsonl(path: Path, start: dt.date) -> int:
    total = 0
    kept = 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            total += 1
            row = json.loads(line)
            when = parse_when(row.get("created_at") or row.get("date") or row.get("created"))
            if in_window(when, start):
                kept += 1
    return kept if start != YEAR_START else total


def search_count(repo: str, start: dt.date, extra: str) -> int:
    total, _items = b.search_range(repo, start, END, extra, 1)
    return total


def main() -> None:
    cases = load_cases()
    windows = {
        "one_year": {"start": YEAR_START.isoformat(), "end": END.isoformat()},
        "six_months": {"start": SIX_START.isoformat(), "end": END.isoformat()},
    }
    if "--samples-only" in sys.argv:
        previous = json.loads((ROOT / "docs" / "data" / "windows-latest.json").read_text(encoding="utf-8"))
        population = previous["population"]
        samples = {}
        for key, bounds in (("one_year", YEAR_START), ("six_months", SIX_START)):
            samples[key] = {name: tally(rows, bounds) for name, rows in cases.items()}
            samples[key]["airflow_issues"] = count_jsonl(ROOT / "corpus" / "ai-year" / "issues-all.jsonl", bounds)
            samples[key]["airflow_mail_messages"] = count_jsonl(ROOT / "corpus" / "ai-year" / "mail-index.jsonl", bounds)
        doc = {
            "schema_version": 1,
            "generated_at": b.now_iso(),
            "windows": windows,
            "note": (
                "samples are the stored benchmark rows whose date falls in the window. "
                "Airflow proof rows only have a month, so the day is treated as the 22nd. "
                "population is GitHub search total_count. Neither number is a census of AI-authored changes, "
                "and Generated-by includes template text on some projects."
            ),
            "samples": samples,
            "population": population,
        }
        dest = ROOT / "docs" / "data" / "windows-latest.json"
        dest.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        print(json.dumps(samples, indent=2), flush=True)
        return
    samples = {}
    for key, bounds in (("one_year", YEAR_START), ("six_months", SIX_START)):
        samples[key] = {name: tally(rows, bounds) for name, rows in cases.items()}
        samples[key]["airflow_issues"] = count_jsonl(ROOT / "corpus" / "ai-year" / "issues-all.jsonl", bounds)
        samples[key]["airflow_mail_messages"] = count_jsonl(ROOT / "corpus" / "ai-year" / "mail-index.jsonl", bounds)

    population = {"one_year": {}, "six_months": {}}
    for name, repo in REPOS:
        for key, start in (("one_year", YEAR_START), ("six_months", SIX_START)):
            row = {"repo": repo}
            for field, extra in EXTRAS:
                row[field] = search_count(repo, start, extra)
            if name == "airflow":
                row["generated_by_tool"] = {
                    tool: search_count(repo, start, f'is:pr "Generated-by: {tool}"')
                    for tool in AIRFLOW_TOOLS
                }
            population[key][name] = row
            print(key, json.dumps(row), flush=True)

    doc = {
        "schema_version": 1,
        "generated_at": b.now_iso(),
        "windows": windows,
        "note": (
            "samples are the stored benchmark rows whose date falls in the window. "
            "Airflow proof rows only have a month, so the day is treated as the 22nd. "
            "population is GitHub search total_count. Neither number is a census of AI-authored changes, "
            "and Generated-by includes template text on some projects."
        ),
        "samples": samples,
        "population": population,
    }
    dest = ROOT / "docs" / "data" / "windows-latest.json"
    dest.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print("wrote", dest, flush=True)


if __name__ == "__main__":
    main()
