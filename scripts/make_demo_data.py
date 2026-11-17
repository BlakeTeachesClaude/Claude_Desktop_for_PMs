"""Regenerates sample/snapshot.json: fictional demo data shaped exactly like a real `make sync` snapshot.

Deterministic (fixed anchor date), no network, no real people. Edit SPEC to change the demo, then run:
    python scripts/make_demo_data.py
Tests check that this file's output matches sample/snapshot.json and that every field the real sync
requests from GitHub is present, so PMs can build and test their own Artifact against it first.
"""
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = dt.datetime(2026, 11, 17, 12, 0, 0, tzinfo=dt.timezone.utc)
OWNER = "fictional"


def ago(days):
    return (ANCHOR - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ") if days is not None else None


# issue: (title, state, [assignees], [labels], milestone, created_days_ago, updated_days_ago, closed_days_ago, project_status)
# pr:    (title, state, draft, author, review, created_days_ago, updated_days_ago, merged_days_ago, project_status)
SPEC = {
    "demo-storefront": {
        "issues": [
            ("Fix checkout keyboard navigation", "OPEN", ["alex"], ["bug", "accessibility"], "Q4 launch", 21, 2, None, "In Progress"),
            ("Add order-history filtering", "OPEN", [], ["enhancement"], "Q4 launch", 18, 15, None, "Todo"),
            ("Improve empty-cart messaging", "CLOSED", ["alex"], ["copy"], None, 30, 9, 9, "Done"),
            ("Support gift-wrap option at checkout", "OPEN", ["riley", "alex"], ["enhancement"], "Q1 planning", 6, 1, None, "Todo"),
        ],
        "prs": [
            ("Add order history specification", "OPEN", False, "alex", "REVIEW_REQUIRED", 4, 1, None, "In Review"),
            ("Update cart copy", "MERGED", False, "riley", "APPROVED", 12, 9, 9, None),
        ],
    },
    "demo-orders-api": {
        "issues": [
            ("Add idempotency to order creation", "OPEN", ["casey"], ["enhancement", "reliability"], "Q4 launch", 25, 3, None, "In Progress"),
            ("Document order status transitions", "OPEN", [], ["docs"], None, 40, 38, None, "Todo"),
            ("Investigate duplicate webhooks", "CLOSED", ["casey"], ["bug"], "Q4 launch", 33, 7, 7, "Done"),
            ("Rate-limit partner API keys", "OPEN", ["jordan"], ["security"], "Q1 planning", 10, 5, None, "In Progress"),
        ],
        "prs": [
            ("Document webhook retry behavior", "OPEN", True, "casey", None, 5, 2, None, "In Progress"),
            ("Fix retry back-off bug", "OPEN", False, "jordan", "CHANGES_REQUESTED", 8, 3, None, "In Review"),
        ],
    },
    "demo-platform-infra": {
        "issues": [
            ("Improve deployment visibility", "OPEN", ["jordan"], ["enhancement"], "Q4 launch", 28, 6, None, "In Progress"),
            ("Investigate slow CI builds", "OPEN", [], ["investigation"], None, 14, 14, None, "Todo"),
            ("Add staging smoke tests", "CLOSED", ["jordan"], ["testing"], "Q4 launch", 35, 11, 11, "Done"),
        ],
        "prs": [
            ("Add CI metrics checklist", "OPEN", False, "jordan", "APPROVED", 7, 1, None, "In Review"),
        ],
    },
    "demo-product-docs": {
        "issues": [
            ("Define release readiness checklist", "OPEN", ["sam"], ["docs", "process"], "Q4 launch", 16, 4, None, "In Progress"),
            ("Update onboarding guide", "OPEN", [], ["docs"], None, 50, 44, None, "Todo"),
            ("Review sprint goals with stakeholders", "CLOSED", ["sam"], ["process"], "Q4 launch", 20, 8, 8, "Done"),
        ],
        "prs": [
            ("Update release checklist", "OPEN", True, "sam", None, 3, 1, None, "In Progress"),
        ],
    },
}


def build():
    repos, items = [], []
    for name, spec in SPEC.items():
        full, number = f"{OWNER}/{name}", 0
        issues, prs = [], []
        for title, state, who, labels, ms, c, u, cl, status in spec["issues"]:
            number += 1
            issues.append({"number": number, "title": title, "state": state,
                           "assignees": [{"login": a} for a in who], "labels": [{"name": l} for l in labels],
                           "milestone": {"title": ms} if ms else None,
                           "createdAt": ago(c), "updatedAt": ago(u), "closedAt": ago(cl), "url": None})
            if status:
                items.append({"title": title, "status": status, "content": {"type": "Issue", "number": number, "repository": full}})
        for title, state, draft, author, review, c, u, mg, status in spec["prs"]:
            number += 1
            prs.append({"number": number, "title": title, "state": state, "isDraft": draft, "author": {"login": author},
                        "reviewDecision": review, "createdAt": ago(c), "updatedAt": ago(u), "mergedAt": ago(mg), "url": None})
            if status:
                items.append({"title": title, "status": status, "content": {"type": "PullRequest", "number": number, "repository": full}})
        repos.append({"repository": {"nameWithOwner": full, "url": None, "defaultBranchRef": {"name": "main"}},
                      "issues": issues, "pull_requests": prs, "limit_reached": False})
    return {"sample_data": True, "synced_at": ago(0), "record_limit_per_list": 1000, "repositories": repos,
            "projects": [{"owner": OWNER, "number": 1, "data": {"items": items, "totalCount": len(items)}, "limit_reached": False}]}


if __name__ == "__main__":
    out = ROOT / "sample" / "snapshot.json"
    out.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    snap = build()
    n_i = sum(len(r["issues"]) for r in snap["repositories"]); n_p = sum(len(r["pull_requests"]) for r in snap["repositories"])
    print(f"Wrote {out.relative_to(ROOT)}: {len(snap['repositories'])} repos, {n_i} issues, {n_p} PRs, {len(snap['projects'][0]['data']['items'])} project items")
