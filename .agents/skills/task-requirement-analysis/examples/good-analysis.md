## Example: Improving Card Comparison Accessibility

**User**: "The items inside the cards are misaligned, I want to fix them."

**Surface**: "The items inside the cards are misaligned."
  ↓ Deep-dive
**Symptom**: Vertical positions of same metrics (e.g., "Remaining Count") vary between cards.
**Root Cause**: **Information Design** - Lack of vertical alignment makes it hard for users to quickly compare values across different weapons.
**Requirement**: Align core metrics vertically across all list cards to enable intuitive comparison.
**Acceptance Criteria**:
- Core metrics (Remaining Count, Skills) start at the same vertical position across all cards in a list.
- Readability of individual metrics is preserved.
