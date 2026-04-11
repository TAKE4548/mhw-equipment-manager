import re
import os
import sys
from pathlib import Path

# Paths
ICON_PY_PATH = Path("src/components/icons.py")
ICON_DIR = Path("assets/icons")

def lint_icons():
    if not ICON_PY_PATH.exists():
        print(f"Error: {ICON_PY_PATH} not found.")
        return False
    if not ICON_DIR.exists():
        print(f"Error: {ICON_DIR} not found.")
        return False

    # 1. Parse ICON_MAP from py file
    content = ICON_PY_PATH.read_text(encoding="utf-8")
    
    # Extract ICON_MAP block to avoid collision with other dicts like attr_colors
    map_match = re.search(r'ICON_MAP = \{(.*?)\}', content, re.DOTALL)
    if not map_match:
        print(f"Error: ICON_MAP not found in {ICON_PY_PATH}.")
        return False
        
    map_content = map_match.group(1)
    # Simple regex to find "Key": "File"
    pattern = r'"([^"]+)":\s*(?:"([^"]+)"|None)'
    matches = re.findall(pattern, map_content)
    
    icon_map_definitions = {k: v for k, v in matches if v}
    
    # 2. Get actual files in assets/icons (Recursive)
    actual_files = set()
    for f in ICON_DIR.rglob("*"):
        if f.is_file():
            # Get path relative to ICON_DIR
            actual_files.add(f.relative_to(ICON_DIR).as_posix())
    
    errors = []
    
    # Check 1: Defined in code but missing from disk
    for key, filename in icon_map_definitions.items():
        if filename not in actual_files:
            errors.append(f"Defined in ICON_MAP but missing from disk: '{filename}' (Key: {key})")
            
    # Check 2: Exists on disk but not defined in code
    defined_filenames = set(icon_map_definitions.values())
    for filename in actual_files:
        if filename not in defined_filenames:
            errors.append(f"Icon exists on disk but not defined in ICON_MAP: '{filename}'")

    if errors:
        print("Asset Lint Errors (Icons):")
        for err in errors:
            print(f"  [FAIL] {err}")
        return False
    
    print("Asset Lint (Icons): [PASS]")
    return True

if __name__ == "__main__":
    if not lint_icons():
        sys.exit(1)
    sys.exit(0)
