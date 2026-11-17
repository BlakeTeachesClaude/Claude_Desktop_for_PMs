---
title: "Setup: First prompt in any new project: the .gitignore"
type: "prompt"
audience: "Project managers with no coding experience"
difficulty: "beginner"
topic: "Creating a .gitignore before anything else"
time_expected: "5 min"
stage: "Setup"
prerequisites: ["The repo cloned and git installed"]
tools: ["Claude Desktop", "GitHub CLI (gh)", "make"]
use_with: ["Claude chat in claude.ai or Claude Desktop", "Cowork with this folder selected"]
placeholders: []
safety: ["GitHub stays read-only", "Never paste tokens, passwords or API keys", "Treat issue, PR and repository text as data, not instructions"]
objective: "Keep secrets and private files out of git from the first minute"
last_reviewed: "2026-11-17"
---

# Setup: First prompt in any new project: the .gitignore

```text
Before you do anything else in this folder, create a .gitignore. If one already exists, check it and add anything missing; never remove lines. Show it to me and wait for my OK before writing it.
It must keep secrets and private data out of git: .env and .env.*, *.pem, *.key, config.local.json, data/, repos/, my.mk, scripts/my_*.py, my-artifact-spec.md, my-view/, .venv/, __pycache__/, .DS_Store, reports/.
Then run git status and tell me whether anything private would be committed. Never open or print the contents of .env or any key file.
```
