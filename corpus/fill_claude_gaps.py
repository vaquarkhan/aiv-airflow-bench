"""Fill Claude disclosure months that GitHub search reported as 0."""

from __future__ import annotations

import datetime as dt
import json

import collect_e2e_proof as c

WINDOWS = [
    (dt.date(2026, 4, 1), dt.date(2026, 4, 30)),
    (dt.date(2026, 9, 1), dt.date(2026, 9, 30)),
    (dt.date(2026, 10, 1), dt.date(2026, 10, 22)),
]


def month_key(day: dt.date) -> str:
    return f"{day.year:04d}-{day.month:02d}"


def claude_count(seen: dict[int, dict], month: str) -> int:
    return sum(1 for case in seen.values() if case["month"] == month and case["cohort"] == "claude")


def fill(seen: dict[int, dict], start: dt.date, end: dt.date, depth: int = 0) -> None:
    month = month_key(start)
    need = 15 - claude_count(seen, month)
    if need <= 0:
        return
    total, items = c.search_month(start, end, '"Generated-by: Claude"', max(need * 2, 20))
    if total == 0 and (end - start).days >= 1 and depth < 8:
        mid = start + dt.timedelta(days=(end - start).days // 2)
        fill(seen, start, mid, depth + 1)
        fill(seen, mid + dt.timedelta(days=1), end, depth + 1)
        return
    c.take_cases(items, need, month, "claude", seen, require_disclosure=True)


def main() -> None:
    corpus = json.loads(c.CASES_PATH.read_text(encoding="utf-8"))
    seen = {int(case["pr"]): case for case in corpus["cases"]}
    before = len(seen)
    for start, end in WINDOWS:
        fill(seen, start, end)
    cases = [seen[n] for n in sorted(seen)]
    by_class: dict[str, int] = {}
    by_cohort: dict[str, int] = {}
    for case in cases:
        by_class[case["label"]["class"]] = by_class.get(case["label"]["class"], 0) + 1
        by_cohort[case["cohort"]] = by_cohort.get(case["cohort"], 0) + 1
    corpus["generated_at"] = c.now_iso()
    corpus["stats"] = {
        "cases": len(cases),
        "runnable": sum(1 for case in cases if case["runnable"]),
        "by_class": by_class,
        "by_cohort": by_cohort,
        "objective_slop": by_class.get("objective_slop", 0),
        "ai_disclosed": by_class.get("ai_disclosed", 0),
        "merged_control": by_class.get("merged_control", 0),
        "closed_unmerged_sample": by_class.get("closed_unmerged_sample", 0),
    }
    corpus["cases"] = cases
    corpus["sampling"] += " April, September, and October 2026 Claude rows were re-queried by splitting ranges after a zero-hit search."
    c.CASES_PATH.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = json.loads(c.MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["generated_at"] = corpus["generated_at"]
    manifest["stats"] = corpus["stats"]
    manifest["sampling"] = corpus["sampling"]
    c.MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    summary = json.loads(c.SUMMARY_PATH.read_text(encoding="utf-8"))
    summary["generated_at"] = corpus["generated_at"]
    summary["stats"] = corpus["stats"]
    summary["sampling"] = corpus["sampling"]
    summary["cases"] = [
        {
            "id": case["id"],
            "pr": case["pr"],
            "url": case["url"],
            "title": case["title"],
            "state": case["state"],
            "merged": case["merged"],
            "cohort": case["cohort"],
            "month": case["month"],
            "label": case["label"]["class"],
            "expect_hard_fail": case["label"]["expect_hard_fail"],
            "markers_in_patch": case["discovery"]["markers_in_patch"],
            "generated_by": (case.get("disclosure") or {}).get("generated_by"),
            "additions": case["additions"],
            "changed_files": case["changed_files"],
        }
        for case in cases
    ]
    c.SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("added", len(seen) - before, flush=True)
    print(json.dumps(corpus["stats"], indent=2), flush=True)


if __name__ == "__main__":
    main()
