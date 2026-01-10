
import os
import re

DOCS_DIR = 'docs'
TARGET_WIDTH = "512"

def should_process_file(filename):
    if not filename.endswith('.md'):
        return False
    match = re.search(r'Chapter_(\d+)', filename)
    if match:
        num = int(match.group(1))
        return 25 <= num <= 46
    return False

def process_content(content):
    lines = content.split('\n')
    new_lines = []
    i = 0
    modified = False
    
    while i < len(lines):
        line = lines[i]
        
        # Pattern 1: Markdown images ![alt](src)
        md_img_match = re.search(r'!\[(.*?)\]\((.*?)\)', line)
        
        if md_img_match:
            alt_text = md_img_match.group(1)
            src = md_img_match.group(2)
            
            # Special handling for page headers
            if 'page_header.svg' in src:
                alt_text = ""
                # No width for page headers (full width)
                replacement = f'<p align="center">\n  <img src="{src}" alt="{alt_text}">\n</p>'
            else:
                replacement = f'<p align="center">\n  <img src="{src}" alt="{alt_text}" width="{TARGET_WIDTH}">\n</p>'
                
            new_lines.append(replacement)
            modified = True
            i += 1
            continue

        # Pattern 2: Existing HTML <img> tags (including repairing corrupted ones)
        if '<img' in line:
            # We assume one image per line in this documentation style.
            
            # Robust extraction of src and alt using non-greedy regex
            # This handles "src" appearing anywhere in the line
            src_match = re.search(r'src=["\'](.*?)["\']', line)
            src = src_match.group(1) if src_match else ""
            
            # Extract alt. If multiple exist (due to corruption), grab the first valid-looking one or empty.
            # In our corruption case, the first alt was alt="", so we might get that.
            alt_match = re.search(r'alt=["\'](.*?)["\']', line)
            alt = alt_match.group(1) if alt_match else ""
            
            if src:
                if 'page_header.svg' in src:
                    # Page header: No width, empty alt
                    new_tag = f'<img src="{src}" alt="">'
                else:
                    # Content image: Target width, preserve alt
                    new_tag = f'<img src="{src}" alt="{alt}" width="{TARGET_WIDTH}">'
                
                # Preserve indentation
                indent_match = re.match(r'(\s*)', line)
                indent = indent_match.group(1) if indent_match else ""
                
                new_line = indent + new_tag
                
                if new_line != line:
                    modified = True
                    # Debug print for major changes/repairs (optional but helpful logic check)
                    # if len(line) > len(new_line) + 20: 
                    #    print(f"Repaired line: {line.strip()[:30]}...")
                    
                new_lines.append(new_line)
            else:
                # Fallback if src not found
                new_lines.append(line)
            
            i += 1
            continue

        new_lines.append(line)
        i += 1

    return '\n'.join(new_lines) if modified else None

def main():
    count = 0
    for filename in sorted(os.listdir(DOCS_DIR)):
        if should_process_file(filename):
            filepath = os.path.join(DOCS_DIR, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            
            new_content = process_content(content)
            
            if new_content:
                with open(filepath, 'w') as f:
                    f.write(new_content)
                print(f"Updated {filename}")
                count += 1
    
    print(f"Modified {count} files.")

if __name__ == '__main__':
    main()
