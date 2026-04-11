---
name: task-requirement-analysis
description: "Initial requirement intake and deep-dive focusing on Root Cause and Purpose-level Goals."
---

# Requirement Analysis Task

Your goal is to transform vague user feedback into a structured, actionable "Ready" backlog item.

## 1. Compliance (Always ON)
- Strictly follow the **3-Check Protocol** in `GEMINI.md`.
- **LANGUAGE POLICY**: All final reports and implementation plans for requirement updates MUST be in **Japanese**.

## 2. Deep-Dive Framework: Surface to Requirement

**CRITICAL RULE**: Do NOT inspect code files to answer these questions. You must execute this task in two distinct phases. Do NOT output the final template until Phase 2.

### Phase 1: Intake & Discovery
1. **Surface**: What did the user exactly say? (Quote)
2. **Symptom**: What is the immediate observable problem?
3. **Root Cause**: Why is it a problem? (Use UX Classification below)

**[MANDATORY TURN-END]**: If the user only provided a "solution" (e.g., "move this button") without stating the *purpose*, or if you lack sufficient context to determine the Root Cause confidently, you MUST ask clarifying questions to the user and END YOUR TURN. Do not proceed to Phase 2 or output the template.

### Phase 2: Requirement Finalization
Once the user answers your questions and the Root Cause is clear:
4. **Requirement**: What is the purpose-level goal? (Must be independent of specific solutions like "Change CSS" or "Edit cards.py")

### UX Classification (for Root Cause)
- **Information Design**: Grouping, hierarchy, missing data, or comparison issues.
- **Interaction**: Workflow friction, missing feedback, or too many steps.
- **Visual**: Legibility, consistency, or visual hierarchy.

## 3. Backlog Status: new vs. ready

| Status | Definition |
|--------|------------|
| **new** | Intake complete, but goal refinement or AC is still vague. |
| **ready** | Goal is purpose-level, AC is clear, and the user has approved the direction. |

- Do NOT mark as `ready` if the Requirement contains specific technical "solutions" (e.g., "Add a button"). It must be a "goal" (e.g., "Improve access to X").

## 4. Output Template (User Feedback)
*Use this ONLY in Phase 2 when marking as `ready`.*

"I have updated the backlog (REQ-{n}, {status}).
- **Surface**: {user_quote}
- **Root Cause**: {ux_classification} - {detailed_reason}
- **Requirement**: {purpose_goal}
- **Acceptance Criteria**: (List goals to achieve)

Ready to start `/dev`?"
