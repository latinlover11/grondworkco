#!/usr/bin/env python3
import os
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_all_html_files():
    html_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def check_file(filepath):
    issues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    soup = BeautifulSoup(content, 'html.parser')
    
    # Check title
    if not soup.title or not soup.title.string.strip():
        issues.append("Missing or empty title tag")
    
    # Check meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if not meta_desc or not meta_desc.get('content', '').strip():
        issues.append("Missing or empty meta description")
    
    # Check images
    for img in soup.find_all('img'):
        src = img.get('src')
        if not src:
            issues.append("Image missing src attribute")
            continue
        # Check if it's a data URI or absolute URL (skip for now)
        if src.startswith('data:') or src.startswith('http'):
            continue
        # Resolve relative to the file's directory
        img_path = os.path.join(os.path.dirname(filepath), src)
        if not os.path.exists(img_path):
            issues.append(f"Image not found: {src}")
        # Check alt attribute
        if not img.get('alt'):
            issues.append(f"Image missing alt attribute: {src}")
    
    # Check internal links (to other HTML files)
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Skip empty, anchor, mailto, tel, external http links
        if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:') or href.startswith('http'):
            continue
        # Resolve relative to the file's directory
        link_path = os.path.join(os.path.dirname(filepath), href)
        # If it's a directory, assume index.html
        if os.path.isdir(link_path):
            link_path = os.path.join(link_path, 'index.html')
        # If it doesn't have .html extension, add it? We'll check as is and then with .html
        if not os.path.exists(link_path):
            # Try adding .html if not present
            if not href.endswith('.html'):
                link_path_html = link_path + '.html'
                if os.path.exists(link_path_html):
                    continue
            issues.append(f"Link not found: {href}")
    
    # Check for schema.org JSON-LD
    json_ld = soup.find_all('script', type='application/ld+json')
    if not json_ld:
        issues.append("No JSON-LD schema markup found")
    else:
        for script in json_ld:
            if not script.string.strip():
                issues.append("Empty JSON-LD script tag")
            # We could try to parse JSON, but skip for now to avoid complexity
    
    return issues

def main():
    html_files = get_all_html_files()
    if not html_files:
        print("No HTML files found.")
        return
    
    total_issues = 0
    for filepath in html_files:
        rel_path = os.path.relpath(filepath, BASE_DIR)
        issues = check_file(filepath)
        if issues:
            print(f"\n{rel_path}:")
            for issue in issues:
                print(f"  - {issue}")
            total_issues += len(issues)
        else:
            print(f"\n{rel_path}: No issues found.")
    
    print(f"\nTotal issues found: {total_issues}")

if __name__ == '__main__':
    main()