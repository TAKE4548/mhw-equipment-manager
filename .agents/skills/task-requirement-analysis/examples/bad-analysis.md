## Anti-pattern: Solution-First Registration

**User**: "The items inside the cards are misaligned, I want to fix them."

**Surface**: "Fix misalignment."
**Requirement**: Align elements by forcing X-coordinate in CSS.

**Problem**: 
- **Solution-centric**: Specifies "CSS X-coordinate" which is a technical means. This restricts the Architect's ability to find better structural solutions (like using `st.columns`).
- **Surface level**: Does not capture "Comparison accessibility" as the goal.
- **Risk**: Directly conflicts with Streamlit constraints, likely leading to an IMPASSE later.
