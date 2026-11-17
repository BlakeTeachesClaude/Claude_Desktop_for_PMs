---
title: "GitHub primer and code-along"
type: "lab"
audience: "Project managers with no coding experience"
difficulty: "beginner"
topic: "GitHub vocabulary, the folder tree and make sync"
time_expected: "25-35 min"
prerequisites: ["setup.md complete"]
tools: ["GitHub CLI (gh)", "make"]
objective: "Run make sample or make sync and find an issue and a PR in data/snapshot.json."
last_reviewed: "2026-11-17"
---

# GitHub primer and code-along

## Vocabulary
Organization: a collection of people and repos. Repository: code and history. Clone: local copy. Branch: separate line of work. Commit: recorded change. Issue: tracked work. Pull request: proposed change and review. Project: cross-repo planning view. Assignee, label, milestone and status are different dimensions; do not treat them as interchangeable.

## Authenticate together

```sh
gh auth login --scopes read:project
gh auth status
gh auth setup-git
gh repo list BlakeTeachesClaude
gh project list --owner BlakeTeachesClaude
```

Select browser authentication and HTTPS; approve only necessary permissions. If already authenticated, `gh auth refresh -s read:project` can request project access. Enterprise SSO may require authorization. On GitHub Enterprise Server add `--hostname your-host.example.com` to `gh auth login`. No credential files belong in the workspace.

## Build the team folder tree

```sh
git clone https://github.com/BlakeTeachesClaude/Claude_Desktop_for_PMs.git
cd Claude_Desktop_for_PMs
```

No git yet? On the repo page choose **Code**, then **Download ZIP**, unzip it and open a terminal in that folder. Then run `make sample` to confirm everything works before you sign in to anything.

Copy config.json to config.local.json and populate authorized repo names in owner/repo form. Add projects as objects like {"owner":"my-org","number":1}. If no project exists leave the list empty. After demo provisioning, use the demo org's actual project number. For the fictional data use `make sample`.

```sh
make sync
```

Inspect repos/OWNER/REPO and data/snapshot.json. Compare one issue, PR and project row to GitHub. The script pulls clean default-branch copies, fetches metadata and writes an atomic snapshot. It refuses to overwrite dirty clones. Each list is capped at 1,000 records; the dashboard must disclose potential truncation.

Next: [schedule and create an Artifact](prompts.md).
