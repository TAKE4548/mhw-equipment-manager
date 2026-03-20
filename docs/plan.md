# Implementation Plan: MHWs Equipment Manager

**Branch**: `001-mhw-eq-manager` | **Date**: 2026-03-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-mhw-eq-manager/spec.md`

## Summary

A Streamlit-based application to manage and track MHWs Kyogeki Artia weapon skill upgrade tables, allowing users to register, execute, and undo/redo upgrade actions efficiently. Execution dynamically affects all active target records to reflect global progression. Future-proofed with separated business logic and multipage architecture.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: Streamlit, Pandas  
**Storage**: SQLite  
**Testing**: pytest  
**Target Platform**: Local Web Application (Streamlit)  
**Project Type**: Python Web App with Multipage Architecture  
**Performance Goals**: Instant UI updates for counter decrements, lightweight caching.  
**Constraints**: Must strictly separate logic, UI components, and state management.  
**Scale/Scope**: Local single-user MVP, handling table data for Kyogeki Artia weapon skills.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec-Driven**: Does this feature begin with a clear, approved specification? (Yes, `spec.md` is approved)
- [x] **AI-First**: Does the design rely on ADK endpoints rather than duplicating logic in the UI? (N/A for this Streamlit app, we will use separated Logic layer)
- [x] **Separation**: Is the API contract between frontend and backend clearly defined? (Logic separated from UI)
- [x] **Verification**: Are there independent validation steps planned for ADK components before UI integration? (Logic will be independently testable via pytest)
- [x] **Observability**: Are we using structured logging or ADK tracing for new agent capabilities? (Logging will be implemented for the action history and DB operations)

## Project Structure

### Documentation (this feature)

```text
specs/001-mhw-eq-manager/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
# Streamlit Multipage Project Structure
src/
├── logic/              # Pure Python logic, independent of Streamlit
│   ├── equipment.py
│   └── history.py
├── components/         # Streamlit UI reused components
│   └── tables.py
└── database/           # SQLite connection and migrations
    └── sqlite_manager.py

pages/                  # Multipage routing
├── 1_register.py
└── 2_settings.py

app.py                  # Main entry point (View & Execute upgrades)
tests/
└── unit/               # Pytest specs testing logic/ without streamlit
```

**Structure Decision**: The application will use a structured Python package format `src/` combined with Streamlit's native `pages/` support. This maintains full separation of concerns while keeping the architecture simple enough for an MVP.
