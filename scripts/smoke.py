#!/usr/bin/env python3
"""Smoke suite with a GO / CONDITIONAL GO / NO-GO report.

Run before teaching a session:  make smoke
Writes reports/smoke-report.md and reports/smoke-report.json. Exit 0 = GO or CONDITIONAL GO, 1 = NO-GO.
--strict treats CONDITIONAL GO as NO-GO.  Live GitHub sync is not exercised; learners without gh use the sample path.
Statuses: PASS, FAIL, WARN (non-blocking issue), SKIP (not exercised).
A failed *required* check is NO-GO; a failed optional check, a WARN, or a SKIP of a live check is CONDITIONAL GO.
"""
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = []


def check(name, required=True):
    def deco(fn):
        t = time.time()
        try:
            status, detail = fn()
        except Exception as exc:  # a crashing check is a failing check
            status, detail = "FAIL", f"{type(exc).__name__}: {exc}"
        if status == "FAIL" and not required:
            status = "WARN"
        RESULTS.append({"name": name, "required": required, "status": status,
                        "detail": detail, "seconds": round(time.time() - t, 2)})
        return fn
    return deco


def run_checks(live):
    @check("Python 3.9+")
    def _():
        return ("PASS" if sys.version_info >= (3, 9) else "FAIL"), platform.python_version()

    @check("git installed")
    def _():
        p = shutil.which("git")
        return ("PASS", p) if p else ("FAIL", "install Git (setup.md)")

    @check("make installed (or python fallback documented)", required=False)
    def _():
        p = shutil.which("make")
        return ("PASS", p) if p else ("WARN", "no make: use `python scripts/sync.py --sample` (setup.md)")

    @check("GitHub CLI installed (live sync only)", required=False)
    def _():
        p = shutil.which("gh")
        return ("PASS", p) if p else ("WARN", "gh missing: learners can still use make sample")

    @check("GitHub CLI authenticated (live sync only)", required=False)
    def _():
        if not shutil.which("gh"):
            return "SKIP", "gh not installed"
        r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=30)
        return ("PASS", "logged in") if r.returncode == 0 else ("WARN", "run gh auth login for live sync")

    @check("sample sync produces data/snapshot.json")
    def _():
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "sync.py"), "--sample"],
                           capture_output=True, text=True, cwd=ROOT, timeout=60)
        ok = r.returncode == 0 and (ROOT / "data" / "snapshot.json").exists()
        return ("PASS" if ok else "FAIL"), (r.stderr.strip() or "snapshot written")

    @check("snapshot has issues, PRs and project items")
    def _():
        s = json.loads((ROOT / "data" / "snapshot.json").read_text())
        issues = sum(len(r["issues"]) for r in s["repositories"])
        prs = sum(len(r["pull_requests"]) for r in s["repositories"])
        items = sum(len(p["data"]["items"]) for p in s["projects"])
        ok = issues and prs and items
        return ("PASS" if ok else "FAIL"), f"{issues} issues, {prs} PRs, {items} project items"

    @check("config.json is valid and ships empty (no real repos)")
    def _():
        cfg = json.loads((ROOT / "config.json").read_text())
        return ("PASS" if cfg == {"repositories": [], "projects": []} else "FAIL"), json.dumps(cfg)

    @check("private paths are git-ignored")
    def _():
        ignore = (ROOT / ".gitignore").read_text()
        missing = [p for p in ("repos/", "data/", "config.local.json", ".env") if p not in ignore]
        return ("PASS" if not missing else "FAIL"), ("ok" if not missing else f"missing: {missing}")

    @check("workshop docs present")
    def _():
        need = ["README.md", "setup.md", "lab.md", "prompts.md", "instructor-guide.md"]
        missing = [n for n in need if not (ROOT / n).exists()]
        return ("PASS" if not missing else "FAIL"), ("all present" if not missing else f"missing {missing}")

    @check("HTML deck present, self-contained, opens from file://")
    def _():
        import re
        text = (ROOT / "deck" / "index.html").read_text(encoding="utf-8")
        slides = text.count('class="slide"')
        external = re.findall(r'(?:src|href)\s*=\s*["\']https?://[^"\']+', text)
        ok = slides >= 10 and not external
        return ("PASS" if ok else "FAIL"), f"{slides} slides, {len(external)} external references"

    @check("Claude project config present; GitHub writes denied")
    def _():
        perms = json.loads((ROOT / ".claude" / "settings.json").read_text())["permissions"]
        needed = {"Bash(gh issue create:*)", "Bash(gh pr merge:*)", "Bash(gh api:*)", "Bash(gh auth token:*)"}
        ok = (ROOT / "CLAUDE.md").exists() and needed <= set(perms["deny"])
        return ("PASS" if ok else "FAIL"), f"{len(perms['allow'])} allow / {len(perms['ask'])} ask / {len(perms['deny'])} deny"

    @check("guided build present and linked")
    def _():
        ok = (ROOT / "guided-build.md").exists() and "guided-build.md" in (ROOT / "README.md").read_text(encoding="utf-8")
        return ("PASS" if ok else "FAIL"), "guided-build.md"

    @check("offline regression suite passes")
    def _():
        out = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x"],
                             capture_output=True, text=True, cwd=ROOT, timeout=300)
        tail = (out.stdout.strip().splitlines() or ["no output"])[-1]
        return ("PASS" if out.returncode == 0 else "FAIL"), tail

    @check("manual compatibility sign-offs current", required=False)
    def _():
        data = json.loads((ROOT / "compat" / "verified.json").read_text())
        limit, today, problems = data["max_age_days"], dt.date.today(), []
        for surface, info in data["surfaces"].items():
            if not info["last_verified"]:
                problems.append(f"{surface}: never verified")
                continue
            age = (today - dt.date.fromisoformat(info["last_verified"])).days
            if age > limit:
                problems.append(f"{surface}: {age} days old")
        return ("WARN", "; ".join(problems)) if problems else ("PASS", "all surfaces verified recently")


def verdict(strict):
    if any(r["status"] == "FAIL" and r["required"] for r in RESULTS):
        return "NO-GO"
    if any(r["status"] in {"FAIL", "WARN", "SKIP"} for r in RESULTS):
        return "NO-GO" if strict else "CONDITIONAL GO"
    return "GO"


def write_reports(v):
    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    stamp = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    (out / "smoke-report.json").write_text(json.dumps({"verdict": v, "generated": stamp, "results": RESULTS}, indent=2))
    icon = {"PASS": "PASS", "FAIL": "FAIL", "WARN": "WARN", "SKIP": "SKIP"}
    lines = [f"# Smoke report: {v}", "", f"Generated {stamp} on {platform.system()} {platform.release()}", "",
             "| Status | Check | Required | Detail |", "|---|---|---|---|"]
    for r in RESULTS:
        lines.append(f"| {icon[r['status']]} | {r['name']} | {'yes' if r['required'] else 'no'} | {r['detail']} |")
    blockers = [r for r in RESULTS if r["status"] == "FAIL" and r["required"]]
    caveats = [r for r in RESULTS if r["status"] in {"FAIL", "WARN", "SKIP"} and r not in blockers]
    if blockers:
        lines += ["", "## Blockers (fix before teaching)"] + [f"- {r['name']}: {r['detail']}" for r in blockers]
    if caveats:
        lines += ["", "## Caveats (go, but know these)"] + [f"- {r['name']}: {r['detail']}" for r in caveats]
    (out / "smoke-report.md").write_text("\n".join(lines) + "\n")
    return out / "smoke-report.md"


def main():
    strict, live = "--strict" in sys.argv, False
    run_checks(live)
    v = verdict(strict)
    path = write_reports(v)
    for r in RESULTS:
        print(f"[{r['status']:<4}] {r['name']} - {r['detail']}")
    print(f"\nVERDICT: {v}   (report: {path.relative_to(ROOT)})")
    sys.exit(1 if v == "NO-GO" else 0)


if __name__ == "__main__":
    main()
