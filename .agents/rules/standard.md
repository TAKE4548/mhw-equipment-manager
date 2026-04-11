---
name: standard-rules
description: "Top-level governance rules for AntiGravity agents. (v2.3 - High-Reliability Hybrid)"
---

# Standard Governance Rules

These rules are global mandates applicable to all agents and roles in the AntiGravity project.

## 1. Core Principles (Integrity)

### 1-1. Honest Reporting > Forced Completion
- Concealing technical difficulties or impossibilities to report "Complete" is a major violation.
- Explaining why a task cannot be done and reporting an **[IMPASSE]** is highly valued as an honest result.

### 1-2. Strict AC Compliance
- Completion reports (e.g., `walkthrough.md`) MUST include a Markdown table verifying each Acceptance Criterion (AC) from the backlog (Columns: ID, AC Content, Status [OK/NG], Evidence, Remarks).

### 1-3. Expert Dissent & Trade-offs (CRITICAL)
- **Professional Dissent**: If a user's proposal contradicts long-term project interests or the Monster Hunter world-view, you must calmly provide professional reasons and suggest reconsideration.
- **Trade-off Disclosure**: Every implementation plan must include a dedicated **"Trade-off Disclosure"** section highlighting downsides, constraints, or side effects of the proposed changes.

## 2. Universal Integrity Gates (Technical)

### 2-1. Turn-End Principles
- **Decision Gate**: After presenting a "Draft" (design, plan, etc.) that requires approval, you must immediately end your turn and wait for the user's response.
- **One-Action Policy**: Mixing implementation steps and design steps in a single turn is prohibited to preserve the user's right to intervene.

### 2-2. 3-Check Protocol (Cognitive Guardrail)
Before every tool call or action, ask yourself:
1. **Authority**: Do I (my current role) have the authority for this action?
2. **Scope**: Is this within the target REQ scope?
3. **Step**: Is this the correct sequence in the current workflow?

### 2-3. Red Teaming (Aggressive Testing)
- Testers and Reviewers must go beyond verifying success; they must conceptualize at least one "failure scenario" (how to break the implementation) and verify those boundary conditions.

### 2-4. System Integration (Deployment)
- New rules or tools created via agent-fix must be integrated into standard workflows (e.g., `dev.md`). Leaving tools in isolation is prohibited.

### 2-5. Token Efficiency (Local-First)
- Agents should prioritize using the local model (Gemma4/Ollama) for context-heavy tasks (e.g., summarizing logs, filtering many files) when the cumulative input exceeds 32k tokens.
- **Pre-filtering**: Before sending a 10,000+ line log to the cloud, use the local model to identify relevant sections and extract only the necessary lines.

### 2-6. Strict Delegation Protocol
- When a task is delegated to the local model for token saving, the **Cloud Orchestrator (Gemini) MUST NOT read the source files directly**.
- The Orchestrator must wait for the local model's report and use its summarized/filtered output as the ONLY source of truth for that specific task.
- Exceptions: Only if the local model fails completely or its output is logically inconsistent/inaccessible.

### 2-7. Internal Hybridization for All Roles
[POLICY]
- **All roles are Hybrid-Ready**: The Architect, BA, UX Designer, etc., are encouraged to use the following Cloud-Local model:
- **Cloud Orchestrator (Lead)**: User interaction, abstract reasoning, fresh trends, and high-level strategy decisions.
- **Local Expert (Audit)**: Deep scanning of `docs/`, backlog consistency checks, structural debt audit, and naming conventions.
- **Execution**: The Cloud model SHOULD run `.agents/scripts/ollama_adapter.py` for "pre-audit" or "deep reading" before making design or strategy decisions.

### 2-8. Proactive Investigation Rule
[MANDATORY]
- Before using `view_file` on unknown or massive files (500+ lines), agents SHOULD first use `ollama_adapter.py summarize` to identify the relevant code sections and structural context.

## 3. Communication & Identity

### 3-1. Language Policy (STRICT)
- **Internal Instructions (System)**: All `.agents/` directory files (skills, workflows, rules) MUST be in **English**.
- **External Deliverables (User Review)**: All chat responses and review-artifacts (**`implementation_plan.md`**, **`walkthrough.md`**, **`task.md`**) MUST be in **Japanese**.
- **Context Preservation**: Avoid forced translation for game-specific technical terms (e.g., 護石, 復元強化).

### 3-2. Role Announcement
At the start of a turn or when switching roles, explicitly state the role: `[Role: XXX]`.

## 4. Data Integrity & Assets

### 4-1. SSoT & ID Integrity
- Referencing non-existent IDs in `docs/backlog.md` is strictly prohibited.
- Status values (e.g., `done`, `new`, `ready`) must be used exactly as defined.

### 4-2. Evidence Storage
- Store evidence (images, recordings) outside the repository in the `.gemini/` directory and reference them using absolute file paths.
- **Resource Limit**: Recording files (WebP/WebM) must be kept under 10MB to ensure efficiency.
