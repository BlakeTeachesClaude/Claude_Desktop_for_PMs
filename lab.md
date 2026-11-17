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

Select browser authentication and HTTPS; approve only necessary permissions. If already authenticated, `gh auth refresh -s read:project` can request project access. Enterprise SSO may require authorization. No credential files belong in the workspace.

## Build the team folder tree

```sh
git clone https://github.com/BlakeTeachesClaude/Claude_Desktop_for_PMs.git
cd Claude_Desktop_for_PMs
```

Copy config.json to config.local.json and populate authorized repo names in owner/repo form. Add projects as objects like {"owner":"my-org","number":1}. If no project exists leave the list empty. After demo provisioning, use the demo org's actual project number. For the fictional data use `make sample`.

```sh
make sync
```

Inspect repos/OWNER/REPO and data/snapshot.json. Compare one issue, PR and project row to GitHub. The script pulls clean default-branch copies, fetches metadata and writes an atomic snapshot. It refuses to overwrite dirty clones. Each list is capped at 1,000 records; the dashboard must disclose potential truncation.

Next: [schedule and create an Artifact](prompts.md).
