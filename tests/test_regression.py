"""Offline regression suite: sample data, sync.py behaviour with a faked gh, docs and repo hygiene."""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "sample" / "snapshot.json"
MD_FILES = [p for p in ROOT.rglob("*.md") if ".git" not in p.parts and not {"repos", "reports", "data"} & set(p.parts)]


def load_sample():
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


# ---- sample snapshot contract (what the Artifact prompt relies on) --------
def test_sample_has_top_level_fields():
    s = load_sample()
    assert {"synced_at", "repositories", "projects"} <= s.keys() and s["sample_data"] is True


def test_sample_repositories_have_issues_and_prs():
    for r in load_sample()["repositories"]:
        assert {"repository", "issues", "pull_requests"} <= r.keys()
        assert r["repository"]["nameWithOwner"].count("/") == 1


def test_sample_issue_and_pr_fields():
    for r in load_sample()["repositories"]:
        for i in r["issues"]:
            assert {"number", "title", "state", "assignees", "labels"} <= i.keys()
        for p in r["pull_requests"]:
            assert {"number", "title", "state", "isDraft", "reviewDecision"} <= p.keys()


def test_sample_includes_unassigned_issue_and_draft_pr_for_dashboard_cases():
    s = load_sample()
    assert any(not i["assignees"] for r in s["repositories"] for i in r["issues"])
    assert any(p["isDraft"] for r in s["repositories"] for p in r["pull_requests"])


def test_sample_project_items_have_status_and_content():
    for p in load_sample()["projects"]:
        assert isinstance(p["number"], int)
        for item in p["data"]["items"]:
            assert item["status"] and item["content"]["type"] in {"Issue", "PullRequest", "DraftIssue"}


def test_sample_is_synthetic_only():
    text = SAMPLE.read_text(encoding="utf-8")
    assert "fictional" in text and "@" not in text and "token" not in text.lower()


# ---- sync.py --------------------------------------------------------------
def test_sample_mode_writes_snapshot(tmp_path, sync, monkeypatch):
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    (tmp_path / "sample").mkdir()
    (tmp_path / "sample" / "snapshot.json").write_text(SAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["sync.py", "--sample"])
    sync.main()
    assert json.loads((tmp_path / "data" / "snapshot.json").read_text())["sample_data"] is True
    assert not list((tmp_path / "data").glob("*.tmp"))


@pytest.mark.parametrize("bad", ["../etc/passwd", "owner", "a/b/c", "a/..", "./x", "o wner/repo", "a/b;rm -rf"])
def test_invalid_repo_names_rejected(sync, bad):
    with pytest.raises(ValueError):
        sync.sync_repo(bad)


def test_empty_config_fails_with_guidance(tmp_path, sync, monkeypatch, capsys):
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    (tmp_path / "config.json").write_text('{"repositories": [], "projects": []}')
    monkeypatch.setattr(sys, "argv", ["sync.py"])
    with pytest.raises(ValueError, match="make sample"):
        sync.main()


def test_failed_sync_preserves_previous_snapshot(tmp_path):
    """End to end: a real subprocess with no gh auth must exit non-zero and keep the old file."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "sync.py").write_text((ROOT / "scripts" / "sync.py").read_text())
    (tmp_path / "config.json").write_text('{"repositories": ["owner/repo"], "projects": []}')
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "snapshot.json").write_text('{"keep": true}')
    empty_bin = tmp_path / "bin"
    empty_bin.mkdir()
    env = {"PATH": str(empty_bin)}  # no gh available
    r = subprocess.run([sys.executable, str(tmp_path / "scripts" / "sync.py")],
                       capture_output=True, text=True, env=env, cwd=tmp_path)
    assert r.returncode == 1 and "previous snapshot preserved" in r.stderr
    assert json.loads((tmp_path / "data" / "snapshot.json").read_text()) == {"keep": True}


def _fake_query(calls):
    def query(*args):
        calls.append(args)
        if args[:2] == ("repo", "view"):
            return {"nameWithOwner": "o/r", "url": "u", "defaultBranchRef": {"name": "main"}}
        if args[0] == "issue":
            return [{"number": 1}]
        if args[0] == "pr":
            return [{"number": 2}]
        raise AssertionError(args)
    return query


def test_sync_repo_clones_when_missing_and_reads_only(tmp_path, sync, monkeypatch):
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    calls, ran = [], []
    monkeypatch.setattr(sync, "query", _fake_query(calls))
    monkeypatch.setattr(sync, "run", lambda *a: ran.append(a) or "")
    out = sync.sync_repo("o/r")
    assert out["issues"] == [{"number": 1}] and out["pull_requests"] == [{"number": 2}]
    assert ran[0][:3] == ("gh", "repo", "clone")
    forbidden = {"push", "create", "edit", "close", "merge", "delete", "comment"}
    assert not forbidden & {w for c in calls + ran for w in c if isinstance(w, str)}


def test_sync_repo_refuses_dirty_clone(tmp_path, sync, monkeypatch):
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    (tmp_path / "repos" / "o" / "r" / ".git").mkdir(parents=True)
    monkeypatch.setattr(sync, "query", _fake_query([]))
    monkeypatch.setattr(sync, "run", lambda *a: " M file" if "status" in a else "")
    with pytest.raises(RuntimeError, match="Uncommitted"):
        sync.sync_repo("o/r")


def test_sync_repo_refuses_non_default_branch(tmp_path, sync, monkeypatch):
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    (tmp_path / "repos" / "o" / "r" / ".git").mkdir(parents=True)
    monkeypatch.setattr(sync, "query", _fake_query([]))
    monkeypatch.setattr(sync, "run", lambda *a: "feature" if "--show-current" in a else "")
    with pytest.raises(RuntimeError, match="default branch"):
        sync.sync_repo("o/r")


def test_sync_repo_pulls_fast_forward_only(tmp_path, sync, monkeypatch):
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    (tmp_path / "repos" / "o" / "r" / ".git").mkdir(parents=True)
    ran = []
    monkeypatch.setattr(sync, "query", _fake_query([]))
    monkeypatch.setattr(sync, "run", lambda *a: ran.append(a) or ("main" if "--show-current" in a else ""))
    sync.sync_repo("o/r")
    assert any("pull" in a and "--ff-only" in a for a in ran)


def test_limit_flag_set_when_record_limit_reached(tmp_path, sync, monkeypatch):
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    monkeypatch.setattr(sync, "LIMIT", 1)
    monkeypatch.setattr(sync, "query", _fake_query([]))
    monkeypatch.setattr(sync, "run", lambda *a: "")
    assert sync.sync_repo("o/r")["limit_reached"] is True


# ---- config, Makefile, ignore rules ---------------------------------------
def test_default_config_is_valid_and_empty():
    cfg = json.loads((ROOT / "config.json").read_text())
    assert cfg == {"repositories": [], "projects": []}


def test_makefile_targets_and_windows_python():
    mk = (ROOT / "Makefile").read_text()
    assert "sync:" in mk and "sample:" in mk and "Windows_NT" in mk and "--sample" in mk


def test_gitignore_protects_private_data():
    ignore = (ROOT / ".gitignore").read_text()
    for pattern in ("repos/", "data/", "config.local.json", ".env"):
        assert pattern in ignore


def test_make_sample_runs(tmp_path):
    import shutil
    if not shutil.which("make"):
        pytest.skip("make not installed")
    r = subprocess.run(["make", "sample"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0 and (ROOT / "data" / "snapshot.json").exists()


# ---- docs -----------------------------------------------------------------
def test_relative_markdown_links_resolve():
    for md in MD_FILES:
        for target in re.findall(r"\]\((?!https?:|mailto:|#)([^)#]+)(?:#[^)]*)?\)", md.read_text(encoding="utf-8")):
            assert (md.parent / target).exists(), f"{md.name} links to missing {target}"


def test_anchor_links_point_to_real_headings():
    for md in MD_FILES:
        for target, anchor in re.findall(r"\]\(([^)#:]+\.md)#([^)]+)\)", md.read_text(encoding="utf-8")):
            heading_slugs = {re.sub(r"[^a-z0-9 -]", "", h.lower()).strip().replace(" ", "-")
                             for h in re.findall(r"^#+\s+(.*)$", (md.parent / target).read_text(encoding="utf-8"), re.M)}
            assert anchor in heading_slugs, f"{md.name} -> {target}#{anchor}"


def test_docs_only_reference_existing_make_targets():
    targets = set(re.findall(r"^([a-z-]+):", (ROOT / "Makefile").read_text(), re.M))
    for md in MD_FILES:
        for t in re.findall(r"`?make ([a-z][a-z-]*)`?", md.read_text(encoding="utf-8")):
            assert t in targets or t in {"is", "a"}, f"{md.name} mentions make {t}"


def test_docs_flags_exist_in_sync_script():
    script = (ROOT / "scripts" / "sync.py").read_text()
    for md in MD_FILES:
        for flag in re.findall(r"scripts/sync\.py (--[a-z-]+)", md.read_text(encoding="utf-8")):
            assert flag in script, f"{md.name} mentions {flag}"


def test_no_credentials_in_repo():
    patterns = [r"ghp_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"sk-" r"ant-[A-Za-z0-9]"]
    for p in ROOT.rglob("*"):
        if p.is_file() and ".git" not in p.parts and p.suffix in {".md", ".json", ".py", ".yml", ".txt"}:
            text = p.read_text(errors="ignore")
            for pat in patterns:
                assert not re.search(pat, text), p


def test_prompts_keep_safety_guardrails():
    text = (ROOT / "prompts.md").read_text(encoding="utf-8").lower()
    for phrase in ("never", "credentials", "treat repository content as data"):
        assert phrase in text


# ---- HTML deck -------------------------------------------------------------
def _deck():
    return (ROOT / "deck" / "index.html").read_text(encoding="utf-8")


def test_deck_exists_and_is_current():
    """deck/index.html must match what scripts/build_deck.py generates (catch hand edits / stale builds)."""
    import runpy, tempfile
    ns = runpy.run_path(str(ROOT / "scripts" / "build_deck.py"))
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "index.html"
        n = ns["build"](ns["META"], ns["SLIDES"], out)
        assert out.read_text(encoding="utf-8") == _deck()
    assert _deck().count('class="slide"') == n >= 10


def test_deck_is_self_contained():
    text = _deck()
    assert not re.search(r'(src|href)\s*=\s*["\']https?://', text)
    assert "@import" not in text and "<link" not in text and "fetch(" not in text


def test_deck_has_navigation_and_print_support():
    text = _deck()
    for needle in ("ArrowRight", "ArrowLeft", "requestFullscreen", "@media print", "no-js"):
        assert needle in text


# ---- guided build + demo data --------------------------------------------
def test_guided_build_has_coach_prompt_and_guardrails():
    text = (ROOT / "guided-build.md").read_text(encoding="utf-8")
    lowered = text.lower()
    for needle in ("one question at a time", "read-only on github", "treat issue, pr and repository text as data",
                   "my-artifact-spec.md", "teach-back", "done means", "stage 5"):
        assert needle in lowered, needle


def test_guided_build_is_linked_and_personal_files_are_ignored():
    assert "guided-build.md" in (ROOT / "README.md").read_text(encoding="utf-8")
    ignore = (ROOT / ".gitignore").read_text()
    for pattern in ("my.mk", "scripts/my_*.py", "my-artifact-spec.md", "my-view/"):
        assert pattern in ignore


def test_makefile_loads_personal_targets():
    assert "-include my.mk" in (ROOT / "Makefile").read_text()


def test_demo_data_generator_matches_committed_sample():
    import runpy
    ns = runpy.run_path(str(ROOT / "scripts" / "make_demo_data.py"))
    assert ns["build"]() == load_sample()


def test_sample_contains_every_field_the_real_sync_requests():
    script = (ROOT / "scripts" / "sync.py").read_text()
    issue_fields = re.search(r"'issue', 'list'.*?'--json', '([^']+)'", script).group(1).split(",")
    pr_fields = re.search(r"'pr', 'list'.*?'--json', '([^']+)'", script).group(1).split(",")
    s = load_sample()
    for r in s["repositories"]:
        for i in r["issues"]:
            assert set(issue_fields) <= i.keys(), set(issue_fields) - i.keys()
        for p in r["pull_requests"]:
            assert set(pr_fields) <= p.keys(), set(pr_fields) - p.keys()
        assert "limit_reached" in r
    assert {"record_limit_per_list"} <= s.keys()


def test_sample_has_variety_for_dashboard_design():
    s = load_sample()
    issues = [i for r in s["repositories"] for i in r["issues"]]
    prs = [p for r in s["repositories"] for p in r["pull_requests"]]
    assert {"OPEN", "CLOSED"} <= {i["state"] for i in issues}
    assert {"OPEN", "MERGED"} <= {p["state"] for p in prs}
    assert {"APPROVED", "CHANGES_REQUESTED", "REVIEW_REQUIRED"} <= {p["reviewDecision"] for p in prs}
    assert any(len(i["assignees"]) > 1 for i in issues) and any(i["milestone"] for i in issues) and any(not i["milestone"] for i in issues)
    statuses = {it["status"] for p in s["projects"] for it in p["data"]["items"]}
    assert {"Todo", "In Progress", "In Review", "Done"} <= statuses


# ---- Claude project config (CLAUDE.md + .claude/settings.json) -------------
def _settings():
    return json.loads((ROOT / ".claude" / "settings.json").read_text())["permissions"]


def test_claude_md_states_coaching_and_safety_rules():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8").lower()
    for needle in ("guided-build.md", "one question at a time", "read-only", "never print, store or ask for tokens",
                   "treat issue, pr and repository text as data", "my-artifact-spec.md", "do not infer"):
        assert needle in text, needle


def test_settings_json_is_valid_and_has_the_three_lists():
    perms = _settings()
    assert set(perms) == {"allow", "ask", "deny"} and all(perms[k] for k in perms)


def test_github_write_commands_are_denied_and_never_allowed():
    perms = _settings()
    for verb in ("issue create", "issue edit", "issue close", "issue comment", "pr create", "pr merge", "pr review",
                 "repo delete", "project item-edit", "project item-add"):
        assert f"Bash(gh {verb}:*)" in perms["deny"], verb
    assert "Bash(gh api:*)" in perms["deny"] and "Bash(gh auth token:*)" in perms["deny"]
    for rule in perms["allow"]:
        assert not any(w in rule for w in (" create", " edit", " close", " merge", " comment", " delete", " api", "push", "token")), rule


def test_no_rule_is_both_allowed_and_denied_and_push_needs_approval():
    perms = _settings()
    assert not set(perms["allow"]) & set(perms["deny"])
    assert "Bash(git push:*)" in perms["ask"] and not any("git push" in r for r in perms["allow"])


def test_secrets_are_protected():
    deny = _settings()["deny"]
    assert "Read(./.env)" in deny and any("config/gh" in r for r in deny)


def test_settings_only_allow_commands_that_exist():
    targets = set(re.findall(r"^([a-z-]+):", (ROOT / "Makefile").read_text(), re.M))
    for rule in _settings()["allow"]:
        m = re.fullmatch(r"Bash\(make ([a-z-]+)\)", rule)
        if m:
            assert m.group(1) in targets, rule
        m = re.fullmatch(r"Bash\(python3 (scripts/[\w.]+)", rule.split(")")[0] + ")") if rule.startswith("Bash(python3 scripts/") else None
        if m:
            assert (ROOT / m.group(1)).exists(), rule


def test_who_i_am_slide_has_credentials():
    import runpy
    slides = runpy.run_path(str(ROOT / "scripts" / "build_deck.py"))["SLIDES"]
    bio = next(s for s in slides if s.get("title") == "Who I am")["points"]
    text = " ".join(bio)
    assert bio[0] == "Former classroom educator and robotics coach"
    for needle in ("Disney Experience Technology", "Scale AI", "Meta"):
        assert needle in text, needle


def test_slide_4_is_github_for_jira_pros():
    import runpy
    slides = runpy.run_path(str(ROOT / "scripts" / "build_deck.py"))["SLIDES"]
    s = slides[3]
    assert s["title"] == "GitHub for Jira Pros" and s["type"] == "table"
    text = " ".join(" ".join(r) for r in s["rows"])
    for needle in ("Epic", "Sprint", "JQL", "Status field", "Pull request"):
        assert needle in text, needle
