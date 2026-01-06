
import os
import re

DOCS_DIR = "/home/e/Desktop/ai-llm-red-team-handbook/docs"
OUTPUT_FILE = "/home/e/.gemini/antigravity/brain/37362efb-057b-43bb-bd3e-a5f4bc7d3761/artifacts/AI_LLM_Red_Team_Handbook_Full.md"

# Order defined in SUMMARY.md usually, but we can infer from filenames
files = sorted([f for f in os.listdir(DOCS_DIR) if f.startswith("Chapter_") and f.endswith(".md")])

# Move 17_01...17_06 to correct position
# The simple sort might put 17_01 after 17? No, 17 does not exist as standalone file.
# 17_01 vs 18 -> 17 comes before 18.
# 01...09...10... so simple string sort works because of leading zeros.

print(f"[*] Assembling {len(files)} chapters...")

full_content = "# AI Red Team Handbook\n\n_Generated for Pre-Release Review_\n\n---\n\n"

for filename in files:
    path = os.path.join(DOCS_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Add a page break or separator
        full_content += f"\n\n<!-- FILE: {filename} -->\n\n" + content + "\n\n---\n"

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(full_content)

print(f"[+] Written full handbook to {OUTPUT_FILE} ({len(full_content)} bytes)")
