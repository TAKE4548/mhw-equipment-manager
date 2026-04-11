---
name: task-backlog-management
description: "Read, update, or query the project backlog at docs/backlog.md."
---

# Backlog Management Task

## 1. Compliance (Universal Integrity Gates)
- You MUST strictly follow **Gate 1-3: Role Boundary (BA vs. Design Gate)** in `project-conventions/SKILL.md`.

## 2. Backlog Item Format
### REQ-{n}: {title}
- **Type**: enhancement | defect
- **Status**: 
  - `new`: Registered by BA, but Root Cause analysis is still insufficient.
  - `ready`: Requirements and Acceptance Criteria are identified, and the **Design Phase (Step 3/4) can begin**.
  - `in-progress` | `done` | `fix-needed` | `needs-investigation`
- **Current step**: {Step 1-8 | none} (Updated by Dev Coordinator)
- **Priority**: unset | P1 | P2 | P3
- **Surface**: {original statement}
- **Root Cause**: {core issue - ends level}
- **Requirement**: {goal state - ends level}
- **Acceptance criteria**: {testable conditions, NO implementation details}
- **Design doc**: {path or "none"}

## 3. Instructions
- **BA Role**: Register/Detail requirements. Ensure `Acceptance criteria` do not contain implementation solutions.
- **Architect Role**: Check if requirement is `ready` for Step 3 design.

## 4. Rules
- Allocate sequential REQ numbers (e.g. REQ-001) and do not reuse them.
- Do NOT delete items. Only update their status and fields.
- `Current step`: Must be updated at the end of every active step in `/dev`.
- `done`: Append completion date and set `Current step` to `none`.
