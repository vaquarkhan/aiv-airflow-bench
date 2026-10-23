"""Index every apache/airflow pull request in 2025-10-22..2026-10-22.

Stores metadata, the PR body, a disclosure/slop label, and the head SHA.
The patch is not stored: the gate materializes it from the SHA at score time.
Resumes from corpus/airflow-all/cursor.json.
"""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import collect_slop_benches as b

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "corpus" / "airflow-all"
JSONL = OUT / "prs.jsonl"
CURSOR = OUT / "cursor.json"
SUMMARY = ROOT / "docs" / "data" / "airflow-all-latest.json"
START = dt.datetime(2025, 10, 22, tzinfo=dt.timezone.utc)
END = dt.datetime(2026, 10, 23, tzinfo=dt.timezone.utc)
SIX = dt.datetime(2026, 4, 22, tzinfo=dt.timezone.utc)

QUERY = """
query($cursor: String) {
  rateLimit { cost remaining resetAt }
  repository(owner: "apache", name: "airflow") {
    pullRequests(first: 100, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}, states: [OPEN, CLOSED, MERGED]) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title state merged createdAt closedAt mergedAt
        additions deletions changedFiles headRefOid url body
        author { login }
      }
    }
  }
}
"""


def token() -> str:
    return subprocess.check_output(["gh", "auth", "token"], text=True).strip()


def graphql(auth: str, cursor: str | None) -> dict:
    payload = json.dumps({"query": QUERY, "variables": {"cursor": cursor}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={"Authorization": f"bearer {auth}", "Content-Type": "application/json", "User-Agent": "aiv-bench"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        if exc.code in (403, 429, 502, 503) or "rate limit" in body.lower():
            print(f"http {exc.code}, sleeping 20s", flush=True)
            time.sleep(20)
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
        else:
            raise RuntimeError(f"graphql http {exc.code}: {body[:300]}") from exc
    if data.get("errors"):
        raise RuntimeError(str(data["errors"])[:400])
    return data["data"]


def classify(title: str, body: str, merged: bool, state: str) -> str:
    text = f"{title}\n{body}"
    flags = b.text_flags(text)
    disc = b.disclosure(body)
    if flags["slop"]:
        return "ai_slop_discussion"
    if disc["disclosed"]:
        return "ai_disclosed"
    if flags["tool"]:
        return "ai_tool_mention"
    if merged:
        return "merged"
    if state == "CLOSED":
        return "closed_unmerged"
    return "open"


def record(node: dict) -> dict:
    body = node.get("body") or ""
    if len(body) > 80_000:
        body = body[:80_000]
    created = dt.datetime.fromisoformat(node["createdAt"].replace("Z", "+00:00"))
    label = classify(node.get("title") or "", body, bool(node.get("merged")), node.get("state") or "")
    disc = b.disclosure(body)
    flags = b.text_flags(f"{node.get('title') or ''}\n{body}")
    return {
        "number": node["number"],
        "url": node.get("url"),
        "title": node.get("title"),
        "state": node.get("state"),
        "merged": bool(node.get("merged")),
        "created_at": node.get("createdAt"),
        "closed_at": node.get("closedAt"),
        "merged_at": node.get("mergedAt"),
        "user": (node.get("author") or {}).get("login"),
        "additions": node.get("additions"),
        "deletions": node.get("deletions"),
        "changed_files": node.get("changedFiles"),
        "head_sha": node.get("headRefOid"),
        "label": label,
        "generated_by": disc.get("generated_by"),
        "disclosure_signals": disc.get("signals"),
        "slop_terms": flags.get("slop_terms"),
        "tool_terms": flags.get("tool_terms"),
        "in_six_months": created >= SIX,
        "runnable_size": (node.get("additions") or 0) <= 5000 and (node.get("changedFiles") or 0) <= 40,
        "expect_hard_fail": False,
        "body": body,
    }


def seen_numbers() -> set[int]:
    found: set[int] = set()
    if not JSONL.is_file():
        return found
    with JSONL.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                found.add(json.loads(line)["number"])
    return found


def summarize() -> None:
    classes: Counter[str] = Counter()
    tools: Counter[str] = Counter()
    months: Counter[str] = Counter()
    six = Counter()
    n = 0
    runnable = 0
    with JSONL.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            n += 1
            classes[row["label"]] += 1
            months[row["created_at"][:7]] += 1
            if row["in_six_months"]:
                six[row["label"]] += 1
            if row["runnable_size"]:
                runnable += 1
            if row.get("generated_by"):
                tools[row["generated_by"]] += 1
    doc = {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repo": "apache/airflow",
        "window": "2025-10-22..2026-10-22",
        "six_months": "2026-04-22..2026-10-22",
        "rows": n,
        "by_class": dict(classes),
        "six_month_rows": sum(six.values()),
        "six_month_by_class": dict(six),
        "by_month": dict(sorted(months.items())),
        "runnable_size": runnable,
        "generated_by_top": tools.most_common(30),
        "artifact": "corpus/airflow-all/prs.jsonl",
        "note": (
            "Every pull request created in the window. expect_hard_fail is false because "
            "patches are not stored in this index; head_sha is the input the gate uses to "
            "materialize the diff. Generated-by counts here are filled trailers, not the raw search total."
        ),
    }
    SUMMARY.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("rows", "by_class", "six_month_rows", "six_month_by_class", "runnable_size")}, indent=2), flush=True)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    auth = token()
    cursor = None
    if CURSOR.is_file():
        cursor = json.loads(CURSOR.read_text(encoding="utf-8")).get("cursor")
    have = seen_numbers()
    pages = 0
    added = 0
    with JSONL.open("a", encoding="utf-8") as handle:
        while True:
            data = graphql(auth, cursor)
            conn = data["repository"]["pullRequests"]
            nodes = conn["nodes"] or []
            pages += 1
            kept_on_page = 0
            oldest = None
            for node in nodes:
                created = dt.datetime.fromisoformat(node["createdAt"].replace("Z", "+00:00"))
                oldest = created if oldest is None or created < oldest else oldest
                if created < START or created >= END:
                    continue
                if node["number"] in have:
                    continue
                row = record(node)
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                have.add(row["number"])
                added += 1
                kept_on_page += 1
            handle.flush()
            info = conn["pageInfo"]
            cursor = info.get("endCursor")
            CURSOR.write_text(json.dumps({"cursor": cursor, "pages": pages, "rows": len(have)}), encoding="utf-8")
            limit = data.get("rateLimit") or {}
            print(
                f"page {pages} kept {kept_on_page} total {len(have)} oldest {oldest} remaining {limit.get('remaining')}",
                flush=True,
            )
            if oldest is not None and oldest < START:
                break
            if not info.get("hasNextPage"):
                break
            if limit.get("remaining") is not None and int(limit["remaining"]) < 20:
                print("low graphql budget, stopping to resume", flush=True)
                summarize()
                return 0
    summarize()
    print(f"added this run {added}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", flush=True)
        raise SystemExit(1)
