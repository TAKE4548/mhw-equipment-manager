---
description: >
  システム（エージェント）のパフォーマンス低下やルール違反、新しい役割が必要な際に使用します。
  開始コマンド: /agent-fix
---

# Agent Improvement Workflow (/agent-fix)

Use this workflow when the agent system is underperforming, breaking rules, or needs new specialized roles.

Step 1: [Role: Agent Architect]
- Intake: Read the provided conversation log (`overview.txt`) and artifacts (`task.md`, `walkthrough.md`).
- Analysis: 
  - Identify where the agent deviated from the workflow.
  - Identify which role's definition was too vague.
  - Identify framework constraints (e.g., Streamlit side effects) that were ignored.
- Output: A summary of "What went wrong" and "Why the current rules failed".

Step 2: [Role: Agent Architect]
- Design: Propose specific diffs for files in `.agents/skills/` or `.agents/workflows/`.
- Create `implementation_plan.md` explaining the rationale for the upgrade.
- **STOP and wait for user approval.**

Step 3: [Role: Agent Architect]
- Execution: Apply the approved changes to the `.agents/` directory.
- **Cleanup**: Audit related skill files and remove redundant gate instructions that are now covered by `project-conventions/SKILL.md`. 
- Verification: If possible, simulate or walk through how the new rule would have prevented the previous failure.
- Commit the changes with a prefix like `meta: Agent upgrade vX.Y`.

Step 4: [Role: Agent Architect]
- Summary: Present a final `walkthrough.md` explaining the "New Guardrails" added to the system.
