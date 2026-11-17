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

## HTML deck
Open `deck/index.html` in any browser (no server or internet needed). Arrow keys navigate, F fullscreen, O slide overview; print to PDF for handouts. Edit the content in `scripts/build_deck.py`, then run `python scripts/build_deck.py`. A test fails if the deck is out of date.

## Using Claude with this repo
`CLAUDE.md` tells Claude to coach PMs by asking one question at a time and to keep GitHub strictly read-only. `.claude/settings.json` pre-approves the lab commands and read-only `gh` queries, asks before installs, commits and edits to shared lab files, and blocks every `gh` write command, `gh api`, token printing and reading `.env`. Claude Code reads both automatically; verify how Claude Desktop and Cowork apply them before teaching and record it in `compat/verified.json`.
