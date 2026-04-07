---
name: task-backlog-management
description: >
  Read, update, or query the project backlog at docs/backlog.md.
  Use when answering questions about the backlog, changing priority,
  updating item status, or tracking progress across sessions.
---

# Backlog Management Task

## Backlog Item Format

Each item in `docs/backlog.md` must follow this structure:

### REQ-{sequential-number}: {title}
- **Type**: enhancement | defect
- **Status**: new | ready | in-progress | done | fix-needed | needs-investigation
- **Current step**: {Step 1-8 | none}
- **Priority**: unset | P1 | P2 | P3
- **Source**: {original user quote}
- **Problem**: {structured problem statement}
- **Requirement**: {what needs to be true when solved}
- **Acceptance criteria**: {testable conditions}
- **Design doc**: {path or "none"}
- **Triage notes**: {hotfix-triager classification result, if applicable}

## Rules
- Allocate sequential REQ numbers (e.g. REQ-001) and do not reuse them.
- Do NOT delete items. Only update their status and fields.
- `Current step` field must be updated by the Dev Coordinator at the end of every active step during the `/dev` session.
- When moving to `done`, append the completion date and set `Current step` to `none`.
