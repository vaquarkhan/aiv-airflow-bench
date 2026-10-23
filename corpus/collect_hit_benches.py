"""Benches 5-7: Godot, Ghostty, and COSMIC compositor.

These are the projects whose maintainers publicly said AI-written pull
requests were overwhelming review, and whose work lands as GitHub PRs.
Window 2025-10-22..2026-10-22. Stratified sample, not a census.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import collect_slop_benches as b

BENCH = b.BENCH
BOILER = (
    "I have not included any LLM (also known as AI) generated content in this PR, "
    "including code, comments, and descriptions."
)
BOILER_2 = "Use of AI must be disclosed and should include a description of how it was used."

PROJECTS = [
    {
        "id": "godot",
        "bench": 5,
        "repo": "godotengine/godot",
        "why": (
            "On 30 Jun 2026 the Godot Foundation said review was overwhelmed by AI-agent "
            "and AI-written pull requests, that vibe-coded submissions are already an "
            "auto-ban, and that new contributors need permission before a feature or "
            "large refactor. https://godotengine.org/article/contribution-policy-2026/"
        ),
        "population": {"prs": 7589, "closed_unmerged": 1094, "slop_language": 32, "generated_by": 79},
    },
    {
        "id": "ghostty",
        "bench": 6,
        "repo": "ghostty-org/ghostty",
        "why": (
            "On 22 Jan 2026 Mitchell Hashimoto restricted AI-written contributions to "
            "accepted issues and maintainers, and banned repeat low-effort submissions, "
            "after saying bad content was up by about 10x. https://github.com/ghostty-org/ghostty/pull/10412"
        ),
        "population": {"prs": 2492, "closed_unmerged": 447, "slop_language": 9, "generated_by": 27},
    },
    {
        "id": "cosmic",
        "bench": 7,
        "repo": "pop-os/cosmic-comp",
        "why": (
            "On 30 Sep 2026 Jeremy Soller said COSMIC would no longer accept LLM-written "
            "code, comments, or PR text because first-time LLM submissions were unplanned "
            "and rarely accepted. cosmic-epoch itself had 23 PRs in the year; cosmic-comp "
            "is the compositor and had 425. The pop-os org had 4363 PRs in the same window."
        ),
        "population": {"prs": 425, "org_prs": 4363},
    },
]


def scrub(text: str) -> str:
    return (text or "").replace(BOILER, " ").replace(BOILER_2, " ")


_text_flags = b.text_flags
_disclosure = b.disclosure


def text_flags(text: str) -> dict:
    return _text_flags(scrub(text))


def disclosure(body: str) -> dict:
    return _disclosure(scrub(body))


b.text_flags = text_flags
b.disclosure = disclosure


def add_closed(repo: str, seen: dict, pr_dir: Path) -> None:
    for start, end in b.quarters():
        _total, items = b.search_range(repo, start, end, "is:pr is:closed -is:merged", 18)
        kept = 0
        for item in items:
            if kept >= 6:
                break
            number = int(item["number"])
            if number in seen or not item.get("pull_request"):
                continue
            try:
                pr = b.fetch_pr(repo, number, pr_dir / f"{number}.json")
            except Exception as exc:  # noqa: BLE001
                print(f"    skip {repo}#{number}: {exc}", flush=True)
                continue
            if pr.get("too_big") or pr.get("merged") or pr.get("markers_in_patch"):
                continue
            flags = text_flags(f"{pr.get('title') or ''}\n{pr.get('body') or ''}")
            disc = disclosure(pr.get("body") or "")
            if flags["slop"] or disc.get("disclosed"):
                continue
            seen[number] = {
                "id": f"{repo.split('/')[-1]}-{number}",
                "source": "github",
                "repo": repo,
                "kind": "pull_request",
                "number": number,
                "url": pr.get("url"),
                "title": pr.get("title"),
                "state": pr.get("state"),
                "merged": False,
                "created_at": pr.get("created_at"),
                "user": pr.get("user"),
                "cohort": "closed_unmerged",
                "runnable": True,
                "head_sha": pr.get("head_sha"),
                "additions": pr.get("additions"),
                "changed_files": pr.get("changed_files"),
                "disclosure": disc,
                "flags": flags,
                "markers_in_patch": [],
                "label": {
                    "class": "closed_unmerged_sample",
                    "expect_hard_fail": False,
                    "rationale": "Closed without merge. Population sample, not a slop label.",
                },
                "body": (pr.get("body") or "")[:40_000],
                "patch_file": f"prs/{number}.json",
            }
            kept += 1
            print(f"    {repo}#{number} closed_unmerged_sample", flush=True)


def collect(project: dict) -> list[dict]:
    repo = project["repo"]
    pr_dir = b.CORPUS / project["id"] / "prs"
    seen: dict[int, dict] = {}
    for start, end in b.quarters():
        for cohort, extra, cap in (
            ("disclosure_search", 'is:pr "Generated-by:"', 8),
            ("slop_search", '"AI slop" OR "vibe coding" OR "vibe coded" OR "vibe-coded" OR hallucinat', 8),
            ("marker_search", 'is:pr "<<<<<<< SEARCH"', 4),
            ("merged_control", "is:pr is:merged", 6),
        ):
            _total, items = b.search_range(repo, start, end, extra, max(cap * 3, 12))
            kept = 0
            for item in items:
                if b.consider(repo, item, cohort, seen, pr_dir, cap - kept):
                    kept += 1
    add_closed(repo, seen, pr_dir)
    return [seen[n] for n in sorted(seen)]


def main() -> int:
    index_path = BENCH / "docs" / "data" / "multi-bench-latest.json"
    previous = json.loads(index_path.read_text(encoding="utf-8"))
    kept = [row for row in previous.get("benches") or [] if int(row.get("bench") or 0) < 5]
    added = []
    for project in PROJECTS:
        print(f"=== bench {project['bench']} {project['repo']} ===", flush=True)
        cases = collect(project)
        stats = b.write_project(project, cases, [])
        manifest_path = b.CORPUS / project["id"] / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["population_search"] = project["population"]
        manifest["population_note"] = "Search totals from 2026-10-22. Not a census, and not a count of bad patches."
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        added.append({
            "bench": project["bench"],
            "project": project["id"],
            "repo": project["repo"],
            "stats": stats,
            "why": project["why"],
            "population_search": project["population"],
        })
    index_path.write_text(json.dumps({
        "schema_version": 1,
        "generated_at": b.now_iso(),
        "window": b.WINDOW,
        "benches": kept + added,
        "not_a_pr_bench": [
            {
                "repo": "apache/logging-log4j2",
                "why": "Piotr Karwasz, 25 Feb 2026: YesWeHack reports jumped to 17, 20, and 13 in Dec 2025-Feb 2026, against about 20 ordinary Log4j bugs in that quarter. The reports are not GitHub pull requests. https://github.com/apache/logging-log4j2/discussions/4052",
            },
            {
                "repo": "nodejs/node",
                "why": "Security team, Jan 2026: more than 30 HackerOne reports between 15 Dec 2025 and 15 Jan 2026, then a Signal 1.0 bar. The reported flood is the bounty inbox. https://nodejs.org/en/blog/announcements/hackerone-signal-requirement",
            },
        ],
        "note": "Template checklist text is scrubbed before labeling. A raw GitHub search for the phrase AI slop is not a list of affected projects.",
    }, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", flush=True)
        raise SystemExit(1)
