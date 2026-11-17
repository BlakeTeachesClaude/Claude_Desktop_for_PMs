---
title: "Claude Desktop for Project Managers: GitHub Shop Edition"
type: "overview"
audience: "Project managers with no coding experience"
difficulty: "beginner"
topic: "Build a personal PM workspace from GitHub data with Claude"
time_expected: "125 min instructor-led, plus setup time"
prerequisites: ["Ability to install software on your computer"]
tools: ["Claude Desktop", "Cowork", "GitHub CLI (gh)", "make"]
objective: "Leave with your own sync, data pulls and view of your team's work, designed by you."
last_reviewed: "2026-11-17"
---

# Claude Desktop for Project Managers | GitHub Shop Edition

Build a personal PM workspace from scratch in an instructor-led workshop.

**Only prerequisite: ability to install software on your computer.** No coding experience, existing developer tools or preconfigured accounts assumed. We cover accounts, Claude access, installation and authentication during the workshop. Cowork availability depends on account plan and organization policy; sample data and partner practice are available if access is blocked.

## Workshop
1. [What we will learn and instructor-led lesson plan](instructor-guide.md)
2. [Install tools together: Windows and Mac](setup.md)
3. [GitHub primer, folder tree and make sync](lab.md)
4. [Scheduled task and Claude Artifact](prompts.md)
5. [Build your own: Claude interviews you](guided-build.md)
6. [Extension challenges](instructor-guide.md#differentiated-practice)

The common presentation layer is a Claude Artifact. Participants independently extend it as Excel, HTML, an enhanced Artifact or their own format. GitHub is the source of truth.

The fictional sample works before the live demo repos exist. Local clone contents, credentials and snapshots must never be committed to this curriculum repository. [Demo provisioning](demo/README.md).

## Testing and go/no-go
```sh
python -m pip install -r requirements-dev.txt
make test    # offline regression suite (gh is faked; no network or GitHub access)
make smoke   # smoke suite; writes reports/smoke-report.md with GO / CONDITIONAL GO / NO-GO
```
Claude Desktop, Cowork scheduling, Artifacts and Claude Code have no public test API, so `compat/verified.json` records when a person last re-walked each one. Missing or older than 60 days gives CONDITIONAL GO.

## Slides, prompts and demo data
- **Deck:** open `deck/index.html` in any browser (no server or internet needed). Arrow keys navigate, F fullscreen, O slide overview; print to PDF for handouts. Each code-along is two to four slides, and prompt slides have **Copy** buttons.
- **Safety first:** the deck teaches what git, clone, `.gitignore` and secrets are before anything is cloned, and starts every project with a `.gitignore`, then a `CLAUDE.md`.
- **Prompts:** `sample-prompts.md` lists every prompt, and `prompts/` has one file per prompt with front matter (audience, difficulty, topic, time expected). The schedule, Artifact and coach prompts come from `prompts.md` and `guided-build.md`.
- **Demo data:** `make sample` loads fictional data (4 repos, 14 issues, 6 PRs, 19 project items). `scripts/make_demo_data.py` regenerates `sample/snapshot.json` and `demo/seed.json` from one spec.
- **Editing:** change `scripts/build_deck.py` or `scripts/make_demo_data.py`, run them, then `make test`. Tests fail if the deck, prompts, instructor-guide slide table, sample data or seed file are out of date.
- `github-pm-workshop.pptx` is an older PowerPoint version that is no longer updated; use the HTML deck.

## Using Claude with this repo
`CLAUDE.md` tells Claude to coach PMs by asking one question at a time and to keep GitHub strictly read-only. `.claude/settings.json` pre-approves the lab commands and read-only `gh` queries, asks before installs, commits and edits to shared lab files, and blocks every `gh` write command, `gh api`, token printing and reading `.env`. Claude Code reads both automatically; verify how Claude Desktop and Cowork apply them before teaching and record it in `compat/verified.json`.
