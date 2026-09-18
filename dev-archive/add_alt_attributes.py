#!/usr/bin/env python3
import os
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_all_html_files():
    html_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def add_missing_alt_attributes():
    """Add missing alt attributes to images"""
    html_files = get_all_html_files()
    total_fixed = 0
    
    for filepath in html_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        modified = False
        
        for img in soup.find_all('img'):
            if not img.get('alt'):
                # Generate a sensible alt attribute based on context
                src = img.get('src', '')
                if src:
                    # Extract filename without extension
                    filename = os.path.splitext(os.path.basename(src))[0]
                    # Replace hyphens and underscores with spaces
                    alt_text = filename.replace('-', ' ').replace('_', ' ')
                    # Capitalize words
                    alt_text = ' '.join(word.capitalize() for word in alt_text.split())
                    
                    # If it looks like a placeholder or generic name, try to get more context
                    if alt_text.lower() in ['img', 'image', 'photo', 'picture'] or len(alt_text) < 3:
                        # Look for nearby headings or captions
                        parent = img.find_parent(['figure', 'div', 'article', 'section'])
                        if parent:
                            # Look for heading or caption nearby
                            heading = parent.find_previous(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                            if heading:
                                alt_text = heading.get_text().strip()[:100]  # Limit length
                            else:
                                # Try to get from aria-label or title if available
                                aria_label = img.get('aria-label', '')
                                if aria_label:
                                    alt_text = aria_label
                                else:
                                    title = img.get('title', '')
                                    if title:
                                        alt_text = title
                                    else:
                                        alt_text = "Image"  # Fallback
                        else:
                            alt_text = "Image"
                    
                    img['alt'] = alt_text
                    modified = True
                    total_fixed += 1
                    print(f"Added alt='{alt_text}' to image in {os.path.relpath(filepath, BASE_DIR)}: {src}")
                else:
                    # No src attribute - this might be a placeholder for JS
                    img['alt'] = "Image"
                    modified = True
                    total_fixed += 1
                    print(f"Added alt='Image' to image with no src in {os.path.relpath(filepath, BASE_DIR)}")
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))
    
    print(f"\nTotal images fixed: {total_fixed}")

def check_for_empty_src():
    """Check for images with empty src attributes that might be intentional"""
    html_files = get_all_html_files()
    placeholders = []
    
    for filepath in html_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if not src:  # Empty src attribute
                placeholders.append((filepath, img))
    
    if placeholders:
        print("\nImages with empty src attributes (possibly intentional for JS):")
        for filepath, img in placeholders:
            rel_path = os.path.relpath(filepath, BASE_DIR)
            # Show surrounding context
            parent = img.find_parent(['div', 'figure', 'a'])
            context = str(parent)[:200] if parent else str(img)[:200]
            print(f"  - {rel_path}: {context}")
    else:
        print("\nNo images with empty src attributes found.")

def main():
    print("Adding missing alt attributes to images...")
    add_missing_alt_attributes()
    check_for_empty_src()

if __name__ == '__main__':
    main()