# Claude Desktop for Project Managers | GitHub Shop Edition

An instructor-led workshop: build a local workspace for an engineering team's repositories, synchronize project data, schedule refreshes, and create a Claude Artifact to visualize issues, projects and pull requests.

## Quick start

Prerequisites: Git, GitHub CLI (gh), Python 3, Make, Claude Desktop with Cowork. On Windows use a compatible shell with these tools.

```sh
git clone https://github.com/BlakeTeachesClaude/Claude_Desktop_for_PMs.git
cd Claude_Desktop_for_PMs
make sample
```

The sample dataset is fictional. For live data:
```sh
gh auth login --scopes read:project
gh auth status
gh auth setup-git
gh repo list OWNER
gh project list --owner OWNER
```
If already authenticated, use `gh auth refresh -s read:project` if needed. Configure only authorized team repositories and projects in `config.json`; use an empty projects list if none are available. Run `make sync`. The local clones are in `repos/OWNER/REPO/` and the structured snapshot in `data/snapshot.json`.

## Workshop materials

- [Instructor guide and slide outline](instructor-guide.md)
- [Claude prompts](prompts.md)
- [Sync script](scripts/sync.py)
- [Fictional sample data](sample/snapshot.json)
- [Demo organization provisioning](demo/README.md)

## Learning outcomes

1. Understand GitHub repositories, issues, PRs and Projects.
2. Authenticate and assemble a team folder tree.
3. Synchronize data with one repeatable command.
4. Schedule a recurring sync using Cowork.
5. Build a private Claude Artifact from the local snapshot.
6. Extend the presentation layer independently using Excel, HTML or another Artifact.

GitHub is the source of truth. The native Artifact is a snapshot presentation, not a guaranteed live filesystem reader. Import or regenerate from the refreshed JSON. Keep credentials and employer data private; the sync never pushes repository changes. The demo organization repositories will be added separately.
