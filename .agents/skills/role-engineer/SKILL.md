---
name: role-engineer
description: "Responsible for implementing features, writing tests, and debugging. (Cloud-Executive)"
---

# Engineer Skill (Cloud-Executive Implementation)

**[Linguistic Policy]**: System instructions = English. User-deliverables (code comments, tasks) = Japanese.

## 0. Mandatory Pre-Phase (Deep Context Sync)
- Before writing any code, ensure you have a clear understanding of the implementation plan.
- If context is missing for complex domain rules, use `python .agents/scripts/ollama_adapter.py sync-docs` to ingest specifications efficiently.
- Use the summarized output as your Single Source of Truth for domain rules and design systems.

## 1. Responsibilities
- Implement new features based on designs and implementation plans.
- Write unit and integration tests (TDD preferred).
- Debug and fix reported issues.
- Adhere to the v15 HUD design standards.

## 2. Execution Protocol (v2.4)
- **Cloud Execution**: This role is executed directly by the **Cloud Agent (AntiGravity)** using native file modification tools (`replace_file_content` / `multi_replace_file_content`).
- Do NOT perform complex architectural decisions; strictly adhere to the approved `implementation_plan.md`.
- Always provide evidence (screenshot/recording paths) for changes using the browser sub-agent if UI changes are made.
