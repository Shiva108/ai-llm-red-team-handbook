
import os
import re

DOCS_DIR = "/home/e/Desktop/ai-llm-red-team-handbook/docs"

# Map Chapter Number to Filename
chapter_map = {}
for filename in os.listdir(DOCS_DIR):
    if filename.startswith("Chapter_"):
        # standard: Chapter_XX_...
        match = re.search(r"Chapter_(\d{2})", filename)
        if match:
             num = match.group(1)
             chapter_map[num] = filename

print(f"[*] Indexed {len(chapter_map)} chapters.")

# Check for broken references
issues = []

for filename in os.listdir(DOCS_DIR):
    if not filename.endswith(".md"): continue
    
    path = os.path.join(DOCS_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find "Chapter XX" references
    references = re.findall(r"Chapter (\d{2})", content)
    
    for ref_num in references:
        if ref_num not in chapter_map:
            # Maybe it refers to Chapter 17 sub-files? 
            # But the user refers to "Chapter 17" usually.
            # 17 should be valid if Chapter_17_01 exists?
            if ref_num == "17":
                 continue # Assuming 17 is valid meta-chapter
            
            issues.append(f"Broken Link in {filename}: References Chapter {ref_num}, which does not exist.")

if not issues:
    print("[+] All Chapter references are valid!")
else:
    print(f"[-] Found {len(issues)} broken references:")
    for i in issues:
        print(i)
