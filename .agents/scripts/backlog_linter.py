import re
import sys
from pathlib import Path

# Config
BACKLOG_PATH = Path("docs/backlog.md")
SESSION_PATH = Path("docs/session.md")
VALID_STATUSES = {"new", "ready", "in-progress", "fix-needed", "needs-investigation", "done", "archived", "completed"} # completed is legacy but we allow it for now or force migration

def lint_backlog():
    if not BACKLOG_PATH.exists():
        print(f"Error: {BACKLOG_PATH} not found.")
        return False

    content = BACKLOG_PATH.read_text(encoding="utf-8")
    errors = []
    
    # 1. Check for REQ IDs
    req_matches = re.findall(r"### (REQ-\d+):", content)
    seen_ids = set()
    for req_id in req_matches:
        if req_id in seen_ids:
            errors.append(f"Duplicate REQ ID: {req_id}")
        seen_ids.add(req_id)

    # 2. Check Status and Date
    # Pattern to match REQ block contents up to the next REQ
    req_blocks = re.split(r"### REQ-\d+:", content)[1:]
    
    for i, block in enumerate(req_blocks):
        req_id = req_matches[i]
        
        # Extract status
        status_match = re.search(r"- \*\*Status\*\*: ([\w-]+)(?:\s*\((.*?)\))?", block)
        if not status_match:
            errors.append(f"{req_id}: Status not found or malformed.")
            continue
            
        status = status_match.group(1).lower()
        date_str = status_match.group(2)
        
        if status not in VALID_STATUSES:
            errors.append(f"{req_id}: Invalid status '{status}'. Valid: {list(VALID_STATUSES)}")
            
        if status == "done" or status == "completed":
            if not date_str or not re.match(r"\d{4}-\d{2}-\d{2}", date_str):
                errors.append(f"{req_id}: Status is '{status}' but missing or invalid date (YYYY-MM-DD). Found: '{date_str}'")

    if errors:
        print("Backlog Lint Errors:")
        for err in errors:
            print(f"  [FAIL] {err}")
        return False
    
    print("Backlog Lint: [PASS]")
    return True

def lint_session():
    if not SESSION_PATH.exists():
        return True # Not an error
        
    content = SESSION_PATH.read_text(encoding="utf-8")
    active_req_match = re.search(r"- \*\*Active REQ\*\*: (REQ-\d+)", content)
    status_match = re.search(r"- \*\*Status\*\*: (\w+)", content)
    
    if active_req_match and status_match:
        active_req = active_req_match.group(1)
        status = status_match.group(1)
        
        if status == "active":
            # Check if this REQ is 'in-progress' in backlog
            backlog_content = BACKLOG_PATH.read_text(encoding="utf-8")
            req_block = re.search(rf"### {active_req}:.*?- \*\*Status\*\*: ([\w-]+)", backlog_content, re.DOTALL)
            if req_block:
                backlog_status = req_block.group(1).lower()
                if backlog_status != "in-progress":
                    print(f"Warning: Session has active {active_req}, but backlog status is '{backlog_status}' (expected 'in-progress').")

    return True

if __name__ == "__main__":
    b_ok = lint_backlog()
    s_ok = lint_session()
    if not b_ok or not s_ok:
        sys.exit(1)
    sys.exit(0)
