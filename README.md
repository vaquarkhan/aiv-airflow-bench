# aiv-airflow-bench

Labeled product-value bench for **[AIV Integrity Gate](https://github.com/vaquarkhan/aiv-integrity-gate)**.

## Public report (GitHub Pages)

**Live report:** https://vaquarkhan.github.io/aiv-airflow-bench/

Anyone can independently validate:

- Interactive metrics + abandoned PR ledger (filter by label)
- Raw JSON under [`/docs/data`](./docs/data/) (`labeled-latest.json`, `abandoned-labeled-latest.json`, …)
- Claim policy: [`docs/PROOF-CLAIMS.md`](./docs/PROOF-CLAIMS.md)
- Live gate runs on open PRs (Actions) — e.g. [`PR #72`](https://github.com/vaquarkhan/aiv-airflow-bench/pull/72) recreates [`apache/airflow#73096`](https://github.com/apache/airflow/pull/73096) as `ai_disclosed`

## What’s in this repo

| Layer | What |
|-------|------|
| **Labeled 50** | 5 proper / 30 ai-slop / 15 mixed — seeded as PRs for CI |
| **Abandoned recreations** | Real closed-unmerged Airflow diffs under `abandoned/<label>/…` branches |
| **`.aiv` config** | Full gate config used in Actions |

This is **not** apache/airflow. Apache Airflow® is a trademark of the ASF.

## Reproduce locally

Scripts and generation live in the gate repo:

```powershell
# clone https://github.com/vaquarkhan/aiv-integrity-gate
python benchmarks/airflow/scripts/run-labeled-benchmark.py
python benchmarks/airflow/scripts/benchmark-abandoned-labeled.py --limit 60
```

Compare outputs to the JSON published on Pages.
