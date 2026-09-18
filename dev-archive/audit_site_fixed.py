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

def resolve_path(base_dir, path):
    """Resolve a path relative to base_dir, assuming the path is relative to the document root (base_dir)."""
    # If path is absolute (starts with /), make it relative to base_dir
    if path.startswith('/'):
        return os.path.join(base_dir, path.lstrip('/'))
    # Otherwise, treat as relative to base_dir
    return os.path.join(base_dir, path)

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
        # Skip data URIs and absolute URLs
        if src.startswith('data:') or src.startswith('http://') or src.startswith('https://'):
            continue
        # Resolve relative to base_dir (document root)
        img_path = resolve_path(BASE_DIR, src)
        if not os.path.exists(img_path):
            issues.append(f"Image not found: {src}")
        # Check alt attribute
        if not img.get('alt'):
            issues.append(f"Image missing alt attribute: {src}")
    
    # Check internal links (to other HTML files)
    seen_links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Skip empty, anchor-only, mailto, tel, external http links
        if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:') or href.startswith('http://') or href.startswith('https://'):
            continue
        # Split off anchor part
        if '#' in href:
            href_part = href.split('#')[0]
            # If href_part is empty, it's a pure anchor link on the same page -> skip
            if not href_part:
                continue
        else:
            href_part = href
        # Avoid duplicate reporting of the same link in this file
        if href_part in seen_links:
            continue
        seen_links.add(href_part)
        # Resolve relative to base_dir (document root)
        link_path = resolve_path(BASE_DIR, href_part)
        # If it's a directory, assume index.html
        if os.path.isdir(link_path):
            link_path = os.path.join(link_path, 'index.html')
        # If it doesn't have .html extension, we might still want to check if adding .html helps?
        # But we'll just check as is for now.
        if not os.path.exists(link_path):
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