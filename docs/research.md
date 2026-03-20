# Phase 0: Research & Technical Decisions

## Technology Stack Validation
- **Decision**: Python 3.10+ with Streamlit and Pandas
- **Rationale**: User explicitly requested Streamlit for rapid UI development of the MHWs equipment manager MVP. Streamlit is well-suited for data-centric Python applications, and Pandas provides powerful structured data handling.
- **Alternatives considered**: None (User specified).

## Data Storage
- **Decision**: SQLite
- **Rationale**: Perfect for the MVP scope, requires no external database server, and handles the expected structured relational data (weapon types, elements, skills, counts) efficiently.
- **Alternatives considered**: JSON/CSV files (too primitive for concurrent updates or querying), PostgreSQL (overkill for a local single-user MVP).

## State Management (Undo/Redo)
- **Decision**: Streamlit `st.session_state` combined with persistent SQLite reads/writes.
- **Rationale**: The Undo/Redo functionality requires an action stack. We will maintain an `action_history` list in `st.session_state` that records the inverse operations of recent actions. When an action is performed, it is committed to SQLite and its inverse is added to the stack.
- **Alternatives considered**: Pure database history tracking (more complex to implement and manage rollback mechanisms for a simple MVP).

## Application Architecture
- **Decision**: Strictly separated Logic & UI layers within a Multipage Streamlit App.
- **Rationale**: To avoid the standard Streamlit "single script" maintainability issues and prepare for Future Roadmap Phase 2-5, pure logic will reside in `src/logic` and not depend on `streamlit`. UI will stay in `app.py` and `pages/`.
- **Alternatives considered**: Keeping everything in Streamlit scripts (Rejected due to user constraints on maintainability).
