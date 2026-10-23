"""Drop template-only slop labels and add real AI-slop hits."""

from __future__ import annotations

import json
import re
from pathlib import Path

import collect_slop_benches as b

BOILER = re.compile(
    r"(?is)low-effort AI-generated PRs will be closed.{0,120}"
    r"|massive AI generated explanations.{0,160}"
    r"|do not paste\s+massive AI generated explanations.{0,160}"
)
REAL_QUERIES = ['"AI slop"', "hallucinated", '"vibe coding"', '"vibe coded"']


def scrub(text: str) -> str:
    return BOILER.sub(" ", text or "")


def relabel(case: dict) -> dict | None:
    text = scrub(f"{case.get('title') or ''}\n{case.get('body') or ''}")
    flags = b.text_flags(text)
    disc = case.get("disclosure") or b.disclosure(case.get("body") or "")
    markers = case.get("markers_in_patch") or []
    merged = bool(case.get("merged"))
    if markers:
        label = {"class": "objective_slop", "expect_hard_fail": True, "rationale": "Patch contains bench hard markers."}
    elif flags["slop"]:
        label = {
            "class": "ai_slop_discussion",
            "expect_hard_fail": False,
            "rationale": "Slop, hallucination, or vibe-coding language outside the project template.",
        }
    elif disc.get("disclosed"):
        label = {
            "class": "ai_disclosed",
            "expect_hard_fail": False,
            "rationale": "Filled Generated-by or AI checkbox. Disclosure is not a fail label.",
        }
    elif flags["tool"]:
        label = {"class": "ai_tool_mention", "expect_hard_fail": False, "rationale": "Names an LLM tool. Not labeled slop."}
    elif merged and case.get("cohort") == "merged_control":
        label = {"class": "merged_control", "expect_hard_fail": False, "rationale": "Merged control."}
    elif case.get("cohort") == "merged_control" and merged:
        label = {"class": "merged_control", "expect_hard_fail": False, "rationale": "Merged control."}
    else:
        return None
    case = dict(case)
    case["flags"] = flags
    case["label"] = label
    return case


def add_real_hits(project: dict, cases: list[dict]) -> list[dict]:
    seen = {int(c["number"]): c for c in cases}
    pr_dir = b.CORPUS / project["id"] / "prs"
    for phrase in REAL_QUERIES:
        _total, items = b.search_range(
            project["repo"], b.START.date(), b.END.date() - __import__("datetime").timedelta(days=1), phrase, 15, depth=2
        )
        kept = 0
        for item in items:
            before = len(seen)
            if b.consider(project["repo"], item, "slop_search", seen, pr_dir, 12 - kept):
                # consider() labels with the old function, which still treats template AI-generated as slop.
                fixed = relabel(seen[int(item["number"])])
                if fixed is None:
                    seen.pop(int(item["number"]), None)
                else:
                    seen[int(item["number"])] = fixed
                    if len(seen) > before:
                        kept += 1
    return [seen[n] for n in sorted(seen)]


def filter_mail(rows: list[dict]) -> list[dict]:
    kept = []
    for row in rows:
        text = scrub(f"{row.get('subject') or ''}\n{row.get('starter_excerpt') or ''}")
        flags = b.text_flags(text)
        if flags["slop"] or flags["tool"] or "disclos" in text.lower() or "AGENTS.md" in text or "generative" in text.lower():
            row = dict(row)
            row["flags"] = flags
            kept.append(row)
    return kept


def main() -> None:
    index = []
    for project in b.PROJECTS:
        path = b.CORPUS / project["id"] / "cases.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        cases = []
        for case in doc["cases"]:
            fixed = relabel(case)
            if fixed is not None:
                cases.append(fixed)
        cases = add_real_hits(project, cases)
        mail_dir = b.CORPUS / project["id"] / "mail-threads"
        raw_mail = []
        if mail_dir.is_dir():
            raw_mail = [json.loads(p.read_text(encoding="utf-8")) for p in mail_dir.glob("*.json")]
        mail = filter_mail(raw_mail or doc.get("mail_threads") or [])
        # mail_threads in cases.json is the short form. Keep full files and rewrite summary from short rows.
        stats = b.write_project(project, cases, [
            {
                "tid": row.get("tid"),
                "subject": row.get("subject"),
                "epoch": 0,
                "last_epoch": 0,
                "date": row.get("date"),
                "last_date": row.get("date"),
                "replies": row.get("replies"),
                "list": f"dev@{project['list_domain']}" if project.get("list_domain") else None,
                "url": row.get("url"),
                "query": row.get("query"),
                "flags": row.get("flags") or {},
                "disclosure": {},
                "starter_excerpt": "",
            }
            for row in mail
        ])
        index.append({"bench": project["bench"], "project": project["id"], "repo": project["repo"], "stats": stats, "why": project["why"]})
    (b.BENCH / "docs" / "data" / "multi-bench-latest.json").write_text(json.dumps({
        "schema_version": 1,
        "generated_at": b.now_iso(),
        "window": b.WINDOW,
        "benches": [
            {"bench": 1, "project": "airflow", "repo": "apache/airflow", "artifact": "docs/data/e2e-proof-latest.json"},
            *index,
        ],
        "note": "Template boilerplate such as 'Low-effort AI-generated PRs will be closed' and curl's 'do not paste massive AI generated explanations' is not counted as slop.",
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
