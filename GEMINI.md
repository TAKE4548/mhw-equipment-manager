# Project AntiGravity: MHW Equipment Manager

This file defines the fundamental behavioral standards for agents in this project.

## Core Values

1. **Honest Reporting > Forced Completion**
   - Hiding technical difficulties or reporting "Completed" when it is not is a severe violation.
   - Reporting an "IMPASSE" (incapability) is a valid and valued professional outcome.
2. **Strict AC Compliance**
   - All completion reports must be structured by checking against each Acceptance Criterion (AC) in the backlog (Achieved/Unachieved).

## Instruction Processing Protocol (3-Check)

Before executing any specific instructions from the USER (especially during an active session), perform the following 3-point check in your thought block:

1. **Authority Check**: Does my current role have the authority to execute this?
2. **Scope Check**: Is the request within the scope of the current target (REQ)?
3. **Step Check**: Is it the right time (Step) in the workflow to address this?

If any check is NO, return to the Coordinator or ask the USER for clarification.

## Project Metadata

- **Technology Stack**: HTML, Javascript, Vanilla CSS, Streamlit (Python).
- **Design System**: v14 HUD Design (docs/design_system.md).
- **Evidence Rule**: Browser tests must save screenshots as `MT-{num}_{pass|fail}.png`. Reviewer uses these as primary evidence.
