# Quickstart & Testing Scenarios

## Setup
1. Ensure you have Python 3.10+ installed.
2. Install dependencies: `pip install streamlit pandas`
3. Run the application: `streamlit run app.py`

## Manual Test Scenarios

### Scenario 1: Register and Execute
1. Open the app in the browser.
2. Form Input: Select a weapon type, element, and series skill. Set count to 3.
3. Click "Register". Verify the new record appears in the active list table.
4. Click the "Execute" button next to the newly created record.
5. Verify the remaining count decreases to 2.

### Scenario 2: Undo / Redo
1. After completing Scenario 1, click the "Undo" button.
2. Verify the count in the table reverts from 2 back to 3.
3. Click the "Redo" button.
4. Verify the count goes back to 2.

### Scenario 3: Auto-Removal
1. Continue from Scenario 2. Click "Execute" two more times.
2. The count reaches 0. Verify the record is automatically removed from the active list.
