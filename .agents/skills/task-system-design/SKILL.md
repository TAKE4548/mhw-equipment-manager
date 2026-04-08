---
name: task-system-design
description: >
  Create high-level system design for an approved requirement.
  Use when user approves a backlog item for development
  and architect role needs to produce a design document.
---

# System Design Task

## Input
- `docs/backlog.md` (Target requirement selected by the PO)
- `docs/architecture.md` (Current system specifications)

## Output
- `docs/designs/{feature-name}.md` containing:
  - High-level architecture and data flow.
  - Impact scope on existing components.
  - Breakdown of implementation tasks.
  - Testing requirements (Unit vs Manual differentiation).
  - Concrete Acceptance Criteria (derived from the backlog).
- **MANDATORY Gate**: The session MUST pause here for user approval.

## Steps
1. Read `docs/architecture.md` to grasp the current structure.
2. Analyze the delta between the target requirement and the current architecture.
3. Identify the impact scope and document any potential risks.
4. Draft the design document.
5. Present the design to the user as the Dev Coordinator.
6. **PAUSE THOUGHTS**: Do not proceed to implementation plan or coding. Wait for the user to say "Approve" or similar.
