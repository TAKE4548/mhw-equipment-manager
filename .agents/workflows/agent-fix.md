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
  - **Identify Incident**: Specify at least one Conversation ID and Turn/Message where the issue occurred.
  - Identify where the agent deviated from the workflow.
  - Identify which role's definition was too vague.
  - Identify framework constraints (e.g., Streamlit side effects) that were ignored.
- Output: A summary of "What went wrong" and "Why the current rules failed", referencing the specific incident.

Step 2: [Role: Agent Architect]
- Design: Propose specific diffs for files in `.agents/skills/` or `.agents/workflows/`.
- **Integration Plan**: If new tools/linters are created, explicitly state in the plan how they will be integrated into standard workflows (e.g., `dev.md`).
- Create `implementation_plan.md` explaining the rationale for the upgrade.
- **STOP and wait for user approval.**

Step 3: [Role: Agent Architect]
- Execution: Apply the approved changes to the `.agents/` directory.
- **Cleanup**: Audit related skill files and remove redundant gate instructions that are now covered by `project-conventions/SKILL.md` or `standard.md`. 
- **Synchronization**: Update standard workflows (e.g., `dev.md`) to integrate new tools as planned.
- Verification: Simulate or walk through how the new rule would have prevented the specific failure identified in Step 1.
- Commit the changes with a prefix like `meta: Agent upgrade vX.Y`.

Step 4: [Role: Agent Architect]
- Summary: Present a final `walkthrough.md` explaining the "New Guardrails" added to the system.
