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
  - `new`: BAが登録したが、Root Cause の掘り下げが不十分な状態。
  - `ready`: Root Cause が特定され、目的レベルの要求（Requirement）が確定した開発可能状態。
- **Current step**: {Step 1-8 | none}
- **Priority**: unset | P1 | P2 | P3
- **Surface**: {original user quote / raw statement}
- **Symptom**: {observed undesirable behavior or user frustration}
- **Root Cause**: {why it happens / core issue - UX categorized if possible}
- **Requirement**: {the goal state / what needs to be true (ends-level, not means-level)}
- **Acceptance criteria**: {testable conditions, focused on ends}
- **Design doc**: {path or "none"}
- **Triage notes**: {hotfix-triager classification result, if applicable}

## Rules
- Allocate sequential REQ numbers (e.g. REQ-001) and do not reuse them.
- Do NOT delete items. Only update their status and fields.
- `Current step` field must be updated by the Dev Coordinator at the end of every active step during the `/dev` session.
- When moving to `done`, append the completion date and set `Current step` to `none`.
