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

Transform information using the following flow:
1. **Surface**: What did the user exactly say? (Quote)
2. **Symptom**: What is the immediate observable problem?
3. **Root Cause**: Why is it a problem? (Use UX Classification below)
4. **Requirement**: What is the purpose-level goal? (Must be independent of specific solutions like "Change CSS")

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
"I have updated the backlog (REQ-{n}, {status}).
- **Surface**: {user_quote}
- **Root Cause**: {ux_classification} - {detailed_reason}
- **Requirement**: {purpose_goal}
- **Acceptance Criteria**: (List goals to achieve)

Ready to start `/dev`?"
