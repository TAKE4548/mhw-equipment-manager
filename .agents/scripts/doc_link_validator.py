import re
import sys
from pathlib import Path

# Config: Define directories to scan for .md files
DOCS_DIRS = [Path("docs"), Path(".agents")]
ROOT_DIR = Path(".")

def validate_links():
    md_files = []
    for d in DOCS_DIRS:
        if d.exists():
            md_files.extend(list(d.glob("**/*.md")))
            
    # Also include specific root files
    md_files.extend(list(ROOT_DIR.glob("*.md")))

    errors = []
    
    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        # Find file:/// links. Stop at common Markdown/quoted delimiters.
        links = re.findall(r"file:///([^ \n\r\t\"\'\)\>\]\`]+)", content)
        
        for link in links:
            # Clean up potential markdown trailing stuff
            clean_link = link.split("#")[0].strip() # Remove anchors
            
            # Convert URI to Path
            # Most links will be like c:/Users/...
            try:
                # Handle relative-like paths if any
                if ":" not in clean_link and not clean_link.startswith("/"):
                    p = md_file.parent / clean_link
                else:
                    p = Path(clean_link)
                
                if not p.exists():
                    errors.append(f"In {md_file.name}: Link target not found: '{clean_link}'")
            except Exception as e:
                errors.append(f"In {md_file.name}: Malformed link '{clean_link}': {e}")

    if errors:
        print("Doc Link Validation Errors:")
        for err in errors:
            print(f"  [FAIL] {err}")
        return False
    
    print("Doc Link Validation: [PASS]")
    return True

if __name__ == "__main__":
    if not validate_links():
        sys.exit(1)
    sys.exit(0)
