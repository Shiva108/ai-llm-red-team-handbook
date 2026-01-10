
import os
import re

DOCS_DIR = 'docs'

def get_chapter_map():
    chapter_map = {}
    for filename in sorted(os.listdir(DOCS_DIR)):
        if filename.startswith('Chapter_') and filename.endswith('.md'):
            # Extract chapter number
            match = re.search(r'Chapter_(\d+)', filename)
            if match:
                num = int(match.group(1))
                # Extract title from filename (remove Chapter_XX_ and .md)
                # Chapter_25_Advanced_Adversarial_ML.md -> Advanced Adversarial ML
                title_part = filename[len(match.group(0)) + 1 : -3]
                title = title_part.replace('_', ' ')
                chapter_map[num] = {
                    'filename': filename,
                    'title': title
                }
    return chapter_map

def update_chapter(filepath, chapter_map):
    with open(filepath, 'r') as f:
        content = f.read()

    # Find Next Steps section
    # Valid headers: ## Next Steps, ### Next Steps
    lines = content.split('\n')
    new_lines = []
    modified = False
    
    in_next_steps = False
    
    for line in lines:
        if re.match(r'^#+\s+Next Steps', line, re.IGNORECASE):
            in_next_steps = True
            new_lines.append(line)
            continue
            
        if in_next_steps:
             # Stop looking if we hit another header
            if line.startswith('#'):
                in_next_steps = False
                new_lines.append(line)
                continue

            # Check for Chapter links to update
            # Pattern: - [**]Chapter (\d+)[**]: Title - Description
            # Capture spaces/stars optionally
            match = re.search(r'^(\s*-\s*)(?:\*\*)?Chapter (\d+)(?:\*\*)?:\s*(.*?)(?=\s+-\s|$)', line)
            
            if match:
                prefix = match.group(1) # "- "
                chap_num = int(match.group(2))
                current_text_title = match.group(3)
                
                # Check if already linked
                if '[' in line and '](' in line:
                    new_lines.append(line)
                    continue

                if chap_num in chapter_map:
                    target = chapter_map[chap_num]
                    # Format: - [Chapter 25: Advanced Adversarial ML](Chapter_25_Advanced_Adversarial_ML.md)
                    # Preserve description if it exists
                    # The regex captured up to " - " or end of line.
                    # We need to append the rest of the line (description)
                    
                    # Let's rebuild the line
                    # Find where the title ends (separator " - " or end)
                    rest_of_line = line[match.end():]
                    
                    new_line = f"{prefix}[Chapter {chap_num}: {target['title']}]({target['filename']}){rest_of_line}"
                    new_lines.append(new_line)
                    modified = True
                    print(f"Updated Ch {chap_num} link in {os.path.basename(filepath)}")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
             new_lines.append(line)

    if modified:
        with open(filepath, 'w') as f:
            f.write('\n'.join(new_lines))
        return True
    return False

def main():
    chapter_map = get_chapter_map()
    print(f"Found {len(chapter_map)} chapters.")
    
    count = 0
    for filename in sorted(os.listdir(DOCS_DIR)):
        if filename.startswith('Chapter_') and filename.endswith('.md'):
            filepath = os.path.join(DOCS_DIR, filename)
            if update_chapter(filepath, chapter_map):
                count += 1
                
    print(f"Modified {count} files.")

if __name__ == '__main__':
    main()
