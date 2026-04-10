---
name: arch-review
description: >
  Architecture Review for structural debt and complex design decisions.
  Distills "Concerns" into long-term plans.
---

# Architecture Review Workflow (/arch-review)

Used to address structural problems (`ARCH` items) that are too complex for a standard `/dev` session.

## Step 1: Context Analysis [Role: Architect]
- Read `ARCH` items and associated `Concerns` in `docs/backlog.md`.
- Analyze the impact on the current code structure (refer to `docs/architecture.md`).

## Step 2: Option Generation [Role: Architect]
- Propose 2-3 options to address the issue:
  1. **Minimal**: Hack/Workaround to mitigate symptoms.
  2. **Recommended**: Right structural fix (refactoring).
  3. **Ideal**: Full redesign (high cost, high benefit).
  4. **Do Nothing**: Accept the risk and document it.
- Present Trade-offs (Time vs. Stability vs. Performance).

## Step 3: USER Decision [Role: Dev Coordinator]
- Present choices to the USER.
- Wait for a final decision. **Do not rush.**

## Step 4: Backlog Refinement
- Update `ARCH` item to `Status: decided`.
- Create corresponding `REQ` items for the chosen implementation path.
