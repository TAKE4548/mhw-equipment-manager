# Technical Design: Lean UI (REQ-007)

## Overview
This document outlines the technical implementation for streamlining the UI and optimizing visual density across the MHW Equipment Manager.

## Architecture
We will introduce a shared component layer to standardize the header and global styling.

### 1. Header Componentization
A new `src/components/common.py` will provide `render_lean_header`.
- **Inputs**: `title` (str), `description` (str), `icon` (str).
- **Behavior**: 
    - Use `st.columns` to layout the title and Undo/Redo controls on the same horizontal line.
    - Check session state for `undo_stack` and `redo_stack` availability.
    - Handle `st.rerun()` upon button clicks.

### 2. Styling Strategy
A new CSS-only injection will be added to `src/components/cards.py` (or a dedicated `src/components/styles.py`).
- **Target**: `[data-testid="stVerticalBlock"] > div` (Gap reduction).
    - **Revised**: `gap: 2px` is strictly for list containers. Standard functional areas (forms/tabs) must retain `16px (1rem)` gaps.
- **Target**: `[data-testid="stExpander"]` (Padding reduction).
- **Target**: `.stDivider` (Hide or thin out).
- **NEW [Polish]**:
    - Header top padding: `2.5rem`
    - Lean separator margins: `1.5rem 0`
    - Heading margins: `1.2rem top / 0.5rem bottom`

## Data Flow
No changes to the data model. The history logic (`src/logic/history.py`) remains the same.

## Testing Requirements
- **Visual**: Verify that titles and Undo/Redo are aligned.
- **Functional**: Ensure Undo/Redo still work correctly when clicked in the new header.
- **Regression**: Ensure `st.fragment` boundaries are not broken by the new shared component (header should generally stay outside fragments or be carefully managed).
