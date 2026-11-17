---
title: "Install together"
type: "setup"
audience: "Project managers with no coding experience"
difficulty: "beginner"
topic: "Install git, gh, make, Python and Claude Desktop on macOS or Windows"
time_expected: "20-30 min"
prerequisites: ["A GitHub account (github.com/signup)"]
tools: ["Homebrew", "winget", "git", "GitHub CLI (gh)", "make", "Claude Desktop"]
objective: "Every learner can run git --version, gh --version and make --version."
last_reviewed: "2026-11-17"
---

# Install together

The only prerequisite is the ability to install software. Start with an empty machine. Explain the terminal, package managers and what each package does.

## Windows (PowerShell)

```powershell
winget --version
winget install --id Git.Git -e
winget install --id GitHub.cli -e
winget install --id Python.Python.3.13 -e
winget search --id GnuWin32.Make
winget install --id GnuWin32.Make -e
winget install --id Anthropic.Claude -e
```

If WinGet is missing, install Microsoft App Installer. Use an approved alternative package manager or the official download if necessary. Reopen PowerShell to refresh PATH. If make is unavailable, use the equivalent `python scripts/sync.py` and `python scripts/sync.py --sample` while resolving installation.

## macOS (Terminal)

Install Homebrew from https://brew.sh if absent; follow its shell setup instructions.

```sh
xcode-select --install   # Apple's command line tools: includes make
brew install git gh python
brew install --cask claude
```

## Check installations

```sh
git --version
gh --version
make --version
python3 --version
```

On Windows check `python --version` instead. Open Claude Desktop, sign in or create an account, and confirm Cowork is available. Create a GitHub account if needed. Never share login tokens with the class or Claude. If your account cannot access Cowork or live GitHub, pair up and use the sample dataset.

Links: https://cli.github.com/ | https://brew.sh | https://claude.com/download | https://github.com/signup
