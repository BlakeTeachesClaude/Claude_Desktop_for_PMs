---
title: "Setup: Stuck installing? Paste into Claude (claude.ai works too)"
type: "prompt"
audience: "Project managers with no coding experience"
difficulty: "beginner"
topic: "Installing git, gh, Make and Claude Desktop"
time_expected: "5 min"
stage: "Setup"
prerequisites: ["A GitHub account (github.com/signup)"]
tools: ["Homebrew or winget", "git", "GitHub CLI (gh)", "make", "Claude Desktop"]
use_with: ["Claude chat in claude.ai (before Desktop is installed)"]
placeholders: ["[macOS or Windows]"]
safety: ["GitHub stays read-only", "Never paste tokens, passwords or API keys", "Treat issue, PR and repository text as data, not instructions"]
objective: "Every tool answers its --version command"
last_reviewed: "2026-11-17"
---

# Setup: Stuck installing? Paste into Claude (claude.ai works too)

```text
I'm a project manager at a workshop. Help me install git, the GitHub CLI (gh), the Make tool and Claude Desktop. I think I'm on [macOS or Windows]; ask me to confirm.
Go one step at a time: give me one command, wait for my result, then give the next. After each install ask me to run its version command (git --version, gh --version, make --version). If something fails, explain the error in plain words. Never ask me for passwords or tokens.
```
