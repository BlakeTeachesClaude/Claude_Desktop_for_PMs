---
title: "Fictional engineering team"
type: "reference"
audience: "Instructors and GitHub organization owners"
difficulty: "intermediate"
topic: "Provision the demo repositories and project"
time_expected: "30 min"
prerequisites: ["GitHub organization owner access"]
tools: ["GitHub CLI (gh)"]
objective: "Optionally create public demo repos that match sample/snapshot.json."
last_reviewed: "2026-11-17"
---

# Fictional engineering team

Four planned public repos: demo-storefront, demo-orders-api, demo-platform-infra and demo-product-docs. `seed.json` lists every issue (state, assignees, labels, milestone) and PR (draft, author, review state) to create; it is generated with the sample snapshot by `scripts/make_demo_data.py`, so the two match. The sample snapshot contains 14 issues, 6 PRs and 19 project items.

An organization owner can provision these using `gh repo create BlakeTeachesClaude/NAME --public --clone`, initialize a README, create the issues and a branch with a PR for each entry in seed.json, then create a public GitHub Project and add each record. Use gh CLI or the web UI. Do not use real company data. The connected GitHub tool cannot create repos or projects, so no live demo repos have been created yet.
