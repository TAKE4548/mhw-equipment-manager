---
name: agent-fix
description: "Workflow for addressing agent performance issues, rule violations, or creating new roles. Command: /agent-fix"
---

# Agent Improvement Workflow (/agent-fix)

Use this workflow when the agent system is underperforming, breaking rules, or needs new specialized roles.

## Step 1: Intake & Analysis [Role: Agent Architect]
- **Intake**: Read the provided conversation log (`overview.txt`) and artifacts (`task.md`, `walkthrough.md`).
- **Analysis**: 
  - **Identify Incident**: Specify at least one Conversation ID and Turn/Message where the issue occurred.
  - Identify where the agent deviated from the workflow.
  - Identify which role's definition was too vague.
  - Identify framework constraints (e.g., Streamlit side effects) that were ignored.
- **Output**: A summary in Japanese of "What went wrong" and "Why the current rules failed," referencing the specific incident.

## Step 2: Design & Planning [Role: Agent Architect]
- **Design**: Propose specific diffs for files in `.agents/skills/` or `.agents/workflows/`.
- **Linguistic Gatekeeping**: Ensure all internal instructions are in English, while user-facing outputs are in Japanese.
- **Integration Plan**: If new tools/linters are created, explicitly state how they will be integrated into standard workflows (e.g., `dev.md`).
- Create `implementation_plan.md` (in Japanese) explaining the rationale for the upgrade.
- **MANDATORY TURN-END**: Wait for user approval.

## Step 3: Execution & Verification [Role: Agent Architect]
- **Execution**: Apply the approved changes to the `.agents/` directory.
- **Cleanup**: Audit related skill files and remove redundant or conflicting instructions.
- **Synchronization**: Update standard workflows (e.g., `dev.md`) to integrate new changes.
- **Verification**: Simulate or walk through how the new rule would have prevented the failure identified in Step 1.
- **Commit**: Prefix the commit message with `meta: Agent upgrade vX.Y`.

## Step 4: Summary [Role: Agent Architect]
- **Final Report**: Present a `walkthrough.md` (in Japanese) explaining the "New Guardrails" added to the system.
