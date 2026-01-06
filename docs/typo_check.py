
import re

TARGET_FILE = "/home/e/.gemini/antigravity/brain/37362efb-057b-43bb-bd3e-a5f4bc7d3761/artifacts/AI_LLM_Red_Team_Handbook_Full.md"

COMMON_TYPOS = {
    "teh": "the",
    "recieve": "receive",
    "seperate": "separate",
    "occured": "occurred",
    "accomodate": "accommodate",
    "definately": "definitely",
    "modle": "model",
    "languge": "language",
    "inteligence": "intelligence",
    "vunerability": "vulnerability"
}

with open(TARGET_FILE, 'r') as f:
    content = f.read()

found = []
for typo, correction in COMMON_TYPOS.items():
    # insensitive search
    matches = re.findall(r'\b' + typo + r'\b', content, re.IGNORECASE)
    if matches:
        found.append(f"Found '{typo}' (should be '{correction}') {len(matches)} times.")

if not found:
    print("[+] No common typos found!")
else:
    print(f"[-] Found typos:")
    for msg in found:
        print(msg)
