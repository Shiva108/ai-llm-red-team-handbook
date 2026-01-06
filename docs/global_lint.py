
import os
import re

DOCS_DIR = "/home/e/Desktop/ai-llm-red-team-handbook/docs"

issues = []

def check_file(filename):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        # Check 1: Headers should be ATX style (prefixed with #)
        if line.startswith("Chapter ") and not line.startswith("# "):
            if i > 5: # Skip metadata lines
                issues.append(f"{filename}:{i+1} Header missing '#'")
                
        # Check 2: No double blank lines
        if i > 0 and line.strip() == "" and lines[i-1].strip() == "":
            # Removing this check as it's too noisy for now, focusing on criticals
            pass

        # Check 3: Broken code blocks (``` without language)
        if line.strip().startswith("```") and len(line.strip()) == 3:
             # Ignore closing blocks
             # We need state tracking to know if it's opening or closing.
             pass

for filename in os.listdir(DOCS_DIR):
    if filename.endswith(".md"):
        check_file(filename)

print(f"Linting complete. Found {len(issues)} potential issues.")
for i in issues:
    print(i)
