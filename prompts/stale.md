---
title: "Code along 05: Make it yours: stale work"
type: "prompt"
audience: "Project managers with no coding experience"
difficulty: "intermediate"
topic: "Artifact refinement: stale work"
time_expected: "3 min"
stage: "Code along 05"
prerequisites: ["data/snapshot.json from make sample"]
tools: ["Claude Desktop", "GitHub CLI (gh)", "make"]
use_with: ["Claude chat in claude.ai or Claude Desktop", "Cowork with this folder selected"]
placeholders: []
safety: ["GitHub stays read-only", "Never paste tokens, passwords or API keys", "Treat issue, PR and repository text as data, not instructions"]
objective: "Add a stale filter based on updatedAt"
last_reviewed: "2026-11-17"
---

# Code along 05: Make it yours: stale work

```text
Add a "stale" filter that highlights open issues with no update in 14 days. Use the updatedAt field and show how many days. Don't guess anything the data doesn't contain.
```
