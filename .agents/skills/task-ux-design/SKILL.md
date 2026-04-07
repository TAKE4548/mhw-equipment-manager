---
name: task-ux-design
description: >
  Design the user interface and interaction flow for a requirement.
  Translate abstract usablity needs into concrete UI specifications.
  Use when the developer session dictates a UI/UX change.
---

# UX Design Task

## Use this skill when
- The backlog item involves UI changes, additions, or UX improvements (like reducing the number of clicks).
- Instructed during the `/dev` workflow's design phase (Step 4).

## Input
- `docs/backlog.md` (Target requirement)
- `docs/design_system.md` (Existing design rules, e.g., slim card design)

## Output
- `docs/ui_spec.md` (UI representation, state, and interaction specifications for the feature).
- Optionally, generated image mockups for UI prototypes.

## Steps
1. Analyze the backlog item and identify "what in the current UI is increasing cognitive load".
2. Design a UI pattern solution that adheres to `design_system.md` constraints (e.g., using `st.dialog` or `st.fragment` to avoid full-page reloads and reduce clicks).
3. Update `docs/ui_spec.md` with explicit details on layout, local state, and event triggers.
4. Pass the result to the Dev Coordinator for user approval.
